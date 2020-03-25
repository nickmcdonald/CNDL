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

from enum import Enum

from qtpynodeeditor import FlowScene, PortType

from qtpy.QtCore import QPointF

from ies import MixMethod, LightDirection

from nodes import (PointlightNode,
                   SpotlightNode,
                   NoiseNode,
                   MixNode,
                   DisplayNode)


class Preset(Enum):
    EMPTY = "Empty"
    SPOTLIGHT = "Spotlight"
    LAMPSHADE = "Lamp Shade"
    # FLASHLIGHT = "Flash Light"


def loadPreset(scene: FlowScene, preset: Preset = Preset.EMPTY):
    scene.clear_scene()

    if preset is Preset.EMPTY:
        displayNode = scene.create_node(DisplayNode)
        displayNode.position += QPointF(2000, 500)

    elif preset is Preset.SPOTLIGHT:
        spotlight = scene.create_node(SpotlightNode)
        spotlight.position += QPointF(500, 100)

        noise = scene.create_node(NoiseNode)
        noise.position += QPointF(500, 700)

        mix = scene.create_node(MixNode)
        mix.position += QPointF(1000, 300)
        mix.model.setMixMethod(MixMethod.MULTIPLY)

        display = scene.create_node(DisplayNode)
        display.position += QPointF(1500, 100)

        scene.create_connection(spotlight[PortType.output][0],
                                mix[PortType.input][0])
        scene.create_connection(noise[PortType.output][0],
                                mix[PortType.input][1])
        scene.create_connection(mix[PortType.output][0],
                                display[PortType.input][0])

    elif preset is Preset.LAMPSHADE:
        spotlightUp = scene.create_node(SpotlightNode)
        spotlightUp.position += QPointF(500, 100)
        spotlightUp.model.setLightDiretion(LightDirection.UP)
        spotlightUp.model.setAngle(60)

        spotlightDown = scene.create_node(SpotlightNode)
        spotlightDown.position += QPointF(500, 700)
        spotlightDown.model.setLightDiretion(LightDirection.DOWN)
        spotlightDown.model.setAngle(60)

        spotMix = scene.create_node(MixNode)
        spotMix.position += QPointF(1000, 300)
        spotMix.model.setMixMethod(MixMethod.MAX)

        pointlight = scene.create_node(PointlightNode)
        pointlight.position += QPointF(1000, 800)
        pointlight.model.setIntensity(20)

        pointMix = scene.create_node(MixNode)
        pointMix.position += QPointF(1500, 300)
        pointMix.model.setMixMethod(MixMethod.MAX)

        display = scene.create_node(DisplayNode)
        display.position += QPointF(2000, 319)
        display.model.setLightPositionZ(0)

        scene.create_connection(spotlightDown[PortType.output][0],
                                spotMix[PortType.input][1])
        scene.create_connection(spotlightUp[PortType.output][0],
                                spotMix[PortType.input][0])
        scene.create_connection(spotMix[PortType.output][0],
                                pointMix[PortType.input][0])
        scene.create_connection(pointlight[PortType.output][0],
                                pointMix[PortType.input][1])
        scene.create_connection(pointMix[PortType.output][0],
                                display[PortType.input][0])

    # elif preset is Preset.FLASHLIGHT:
    #     spotlight = scene.create_node(SpotlightNode)
    #     spotlight.position += QPointF(500, 100)
    #     spotlight.model.setLightDiretion(LightDirection.UP)
    #     spotlight.model.setAngle(30)
    #
    #     noise = scene.create_node(NoiseNode)
    #     noise.position += QPointF(500, 700)
    #
    #     mix = scene.create_node(MixNode)
    #     mix.position += QPointF(1000, 300)
    #     mix.model.setMixMethod(MixMethod.MULTIPLY)
    #
    #     display = scene.create_node(DisplayNode)
    #     display.position += QPointF(1500, 100)
    #     display.model.setLightPositionZ(0)
    #     display.model.setLightPositionY(60)
    #     display.model.setLightRotationX(-90)
    #
    #     scene.create_connection(spotlight[PortType.output][0],
    #                             mix[PortType.input][0])
    #     scene.create_connection(noise[PortType.output][0],
    #                             mix[PortType.input][1])
    #     scene.create_connection(mix[PortType.output][0],
    #                             display[PortType.input][0])
