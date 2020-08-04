########################################################
#
# Copyright (C) 2020-2021 Nick McDonald <nick@lazymorninggames.com>
#
# This file is part of CNDL.
#
# CNDL can not be copied and/or distributed without the express
#
# permission of Nick McDonald
########################################################

import os
import time
import base64

from multiprocessing import Process, Value, Event, Manager, Lock
from ctypes import c_char_p

from enum import Enum

from scipy.spatial.transform import Rotation

import pyluxcore as lux


class RenderState(Enum):
    WAITING = 1
    RENDERING = 2
    EDIT = 3

TEMP_DIR = os.getenv('TEMP') + "\cndl"
try:
    os.makedirs(TEMP_DIR)
except:
    print(TEMP_DIR + " Exists")


def luxRender(notify, samples, state, lightTranform, iesFileLock):
    configProps = lux.Properties()
    configProps.SetFromString("""
            renderengine.type = "RTPATHCPU"
            sampler.type = "RTPATHCPUSAMPLER"

            native.threads.count = 2

            path.pathdepth.total = 2

            film.width = 512
            film.height = 512

            filesaver.directory = "{0}"
            film.outputs.0.filename = "{0}/renderimage.png"
            """.format(TEMP_DIR))

    sceneProps = lux.Properties()
    sceneProps.SetFromString("""
            scene.camera.lookat.orig = 0 12.0 3.0
            scene.camera.lookat.target = 0.0 0.0 3.0
            scene.camera.fieldofview = 60

            scene.materials.whitematte.type = matte
            scene.materials.whitematte.kd = 0.75 0.75 0.75

            scene.objects.floor.ply = scenes/basicIES/room.ply
            scene.objects.floor.material = whitematte

            scene.lights.previewIES.type = "mappoint"
            scene.lights.previewIES.transformation = {0}
            scene.lights.previewIES.iesfile = {1}/render.ies
            scene.lights.previewIES.samples = 1
            scene.lights.previewIES.flipz = 1
            """.format(lightTranform[0], TEMP_DIR))

    scene = lux.Scene(sceneProps)
    config = lux.RenderConfig(configProps, scene)
    session = lux.RenderSession(config)

    session.Start()
    while(True):

        if state.value != RenderState.EDIT.value:
            state.value = RenderState.WAITING.value
            wasNotified = notify.wait(10)
            if not wasNotified:
                break
            else:
                state.value = RenderState.EDIT.value
            notify.clear()

        if state.value == RenderState.EDIT.value:
            session.Pause()
            luxcore_scene = session.GetRenderConfig().GetScene()
            session.BeginSceneEdit()

            luxcore_scene.DeleteLight("previewIES")

            props = lux.Properties()
            props.SetFromString("""
                    scene.lights.previewIES.type = "mappoint"
                    scene.lights.previewIES.transformation = {0}
                    scene.lights.previewIES.iesfile = {1}/render.ies
                    scene.lights.previewIES.samples = 1
                    scene.lights.previewIES.flipz = 1
                    """.format(lightTranform[0], TEMP_DIR))

            iesFileLock.acquire()
            luxcore_scene.Parse(props)
            iesFileLock.release()


            session.EndSceneEdit()
            session.Resume()

        state.value = RenderState.RENDERING.value

        try:
            startTime = time.time()
            for i in range(0, 50):
                time.sleep(0.1)
                elapsedTime = time.time() - startTime

                # Print some information about the rendering progress

                # Update statistics
                session.UpdateStats()

                stats = session.GetStats();
                print("[Elapsed time: %3d/3sec][Samples %4d]" % (
                        stats.Get("stats.renderengine.time").GetFloat(),
                        stats.Get("stats.renderengine.pass").GetInt()))

                session.GetFilm().Save()

                if state.value == RenderState.EDIT.value:
                    break
                if stats.Get("stats.renderengine.pass").GetInt() >= 4:
                    state.value = RenderState.WAITING.value
                    break

        except RuntimeError:
            break

    session.Stop()


class Renderer():

    def __init__(self):
        self.state = Value('i', RenderState.WAITING.value)
        self.samples = Value('i', 2)
        self.notify = Event()
        self.renderProcess = None
        manager = Manager()
        self.lightTranform = manager.list([self.getTransform()])
        # self.iesBlob = manager.list([base64.b64encode(b"")])
        self.iesFileLock = Lock()

    def kill(self):
        self.renderProcess.kill()

    def render(self, ies, peakintensity=100,
               position=[0.0, 0.5, 3.0], rotation=[0, 0, 0], samples=2):

        self.lightTranform[0] = self.getTransform(position, rotation)
        # iesBlob = base64.b64encode(bytes(ies.getIesOutput(peakintensity),
        #                            encoding='utf-8'))
        # self.iesBlob[0] = iesBlob.decode("utf-8")

        self.setNewIes(ies, peakintensity)

        if not self.renderProcess or not self.renderProcess.is_alive():
            self.renderProcess = Process(target=luxRender,
                                         args=(self.notify,
                                               self.samples,
                                               self.state,
                                               self.lightTranform,
                                               self.iesFileLock))
            self.renderProcess.start()

        self.samples.value = samples
        if self.state.value == RenderState.WAITING.value:
            self.notify.set()
        else:
            self.state.value = RenderState.EDIT.value

    def setNewIes(self, ies, peakintensity):
        self.iesFileLock.acquire()
        f = open(TEMP_DIR + "/render.ies", "w")
        f.write(ies.getIesOutput(peakintensity))
        f.close()
        self.iesFileLock.release()

    def getTransform(self, position=[0.0, 0.5, 3.0], rotation=[0, 0, 0]):

        rot = Rotation.from_euler('xyz', rotation, degrees=True).as_matrix()

        trans = "{0:.2f} {1:.2f} {2:.2f} 0.0 {3:.2f} {4:.2f} {5:.2f} 0.0 "
        trans += "{6:.2f} {7:.2f} {8:.2f} 0.0 {9:.2f} {10:.2f} {11:.2f} 1.0"
        trans = trans.format(rot[0][0],
                             rot[0][1],
                             rot[0][2],
                             rot[1][0],
                             rot[1][1],
                             rot[1][2],
                             rot[2][0],
                             rot[2][1],
                             rot[2][2],
                             position[0], position[1], position[2])
        return trans
