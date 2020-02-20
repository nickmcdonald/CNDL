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


from multiprocessing import Process

import pyluxcore as lux


def render(ies, samples):
    f = open("scenes/render.ies", "w")
    f.write(str(ies))
    f.close()

    p = Process(target=luxRender, args=(samples,))
    p.start()


def luxRender(samples):
    # Load the configuration from file
    props = lux.Properties("scenes/basicIES/basicIES.cfg")

    # Change the render engine to PATHCPU
    # props.Set(lux.Property("renderengine.type", ["PATHCPU"]))

    config = lux.RenderConfig(props)
    session = lux.RenderSession(config)

    session.Start()

    for x in range(samples):

        session.UpdateStats()
        stats = session.GetStats()

        print("[Elapsed time: %3d/10sec][Samples %4d][Avg. samples/sec % 3.2f]"
              % (
                stats.Get("stats.renderengine.time").GetFloat(),
                stats.Get("stats.renderengine.pass").GetInt(),
                stats.Get("stats.renderengine.total.samplesec").GetFloat()
                / 1000000.0))

        session.GetFilm().Save()

    session.Stop()
