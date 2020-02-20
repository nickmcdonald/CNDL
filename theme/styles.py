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

DEFAULT = '''
{
  "FlowViewStyle": {
    "BackgroundColor": [53, 53, 53],
    "FineGridColor": [60, 60, 60],
    "CoarseGridColor": [25, 25, 25]
  },
  "NodeStyle": {
    "NormalBoundaryColor": [255, 255, 255],
    "SelectedBoundaryColor": [255, 165, 0],
    "GradientColor0": "gray",
    "GradientColor1": [80, 80, 80],
    "GradientColor2": [64, 64, 64],
    "GradientColor3": [58, 58, 58],
    "ShadowColor": [20, 20, 20],
    "FontColor" : "white",
    "FontColorFaded" : "gray",
    "ConnectionPointColor": [169, 169, 169],
    "FilledConnectionPointColor": "cyan",
    "ErrorColor": "red",
    "WarningColor": [128, 128, 0],

    "PenWidth": 1.0,
    "HoveredPenWidth": 1.5,

    "ConnectionPointDiameter": 8.0,

    "Opacity": 0.8
  },
  "ConnectionStyle": {
    "ConstructionColor": "gray",
    "NormalColor": "darkcyan",
    "SelectedColor": [100, 100, 100],
    "SelectedHaloColor": "orange",
    "HoveredColor": "lightcyan",

    "LineWidth": 3.0,
    "ConstructionLineWidth": 2.0,
    "PointDiameter": 10.0,

    "UseDataDefinedColors": false
  }
}
'''
