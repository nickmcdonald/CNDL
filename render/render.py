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


from multiprocessing import Process, Value, Event

from enum import Enum

import pyluxcore as lux

from time import sleep


class RenderState(Enum):
    WAITING = 1
    RENDERING = 2
    INTERRUPT = 3


def luxRender(notify, samples, state):

    while(True):

        if state.value != RenderState.INTERRUPT.value:
            state.value = RenderState.WAITING.value
            print("waiting")
            wasNotified = notify.wait(3)
            if not wasNotified:
                print("killed")
                break
            notify.clear()
        state.value = RenderState.RENDERING.value
        print("rendering")

        try:
            props = lux.Properties("scenes/basicIES/basicIES.cfg")
            config = lux.RenderConfig(props)
            session = lux.RenderSession(config)
            session.Start()
            previousPass = -1
            while True:
                if state.value == RenderState.INTERRUPT.value:
                    break
                session.UpdateStats()
                stats = session.GetStats()

                elapsed = stats.Get("stats.renderengine.time").GetFloat()
                currentPass = stats.Get("stats.renderengine.pass").GetInt()

                if currentPass > previousPass:
                    session.GetFilm().Save()
                    previousPass = currentPass
                    print(currentPass)
                if currentPass >= samples.value or elapsed > 3:
                    break
                sleep(0.1)

            session.Stop()
        except RuntimeError:
            state.value = RenderState.INTERRUPT.value
        finally:
            if session:
                session.Stop()


class Renderer():

    def __init__(self):
        self.state = Value('i', RenderState.WAITING.value)
        self.samples = Value('i', 2)
        self.notify = Event()
        self.renderProcess = None

    def render(self, ies, peakIntensity, samples):
        f = open("scenes/render.ies", "w")
        f.write(ies.getIesOutput(peakIntensity))
        f.close()
        if not self.renderProcess or not self.renderProcess.is_alive():
            self.renderProcess = Process(target=luxRender,
                                         args=(self.notify,
                                               self.samples,
                                               self.state))
            self.renderProcess.start()
            print("started")
        self.samples.value = samples
        if self.state.value == RenderState.WAITING.value:
            self.notify.set()
        else:
            self.state.value = RenderState.INTERRUPT.value
