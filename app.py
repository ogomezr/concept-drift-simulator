"""
This app's interface and plots are heavily inspired from the scikit-learn
Classifier comparison tutorial and dash-svm app . Part of the app's code is
directly taken from it. You canfind it here:
http://scikit-learn.org/stable/auto_examples/classification/plot_classifier_comparison.html
https://github.com/plotly/dash-svm

Autor: Oscar Gomez Ramirez
"""

import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import numpy as np
import visdcc
from modules import DetectChangeAlg
from modules import GenData
import utils.dash_reusable_components as drc


app = dash.Dash(__name__)
app.title = 'Adaptative Algorithm Simulator ( Concept Drift )'
server = app.server
app.config['suppress_callback_exceptions'] = True
app.css.config.serve_locally = False

app.layout = html.Div(style={'overflow':'hidden'},children=[
    # .container class is fixed, .container.scalable is scalable
    html.Div(className="banner", children=[
        html.Div(className='container scalable', children=[
            html.H2(html.A(
                'Adaptative Algorithm Simulator ( Concept Drift )',
                href='https://github.com/ogomezr/Concept-Drift-Simulator',
                style={
                    'text-decoration': 'none',
                    'color': 'inherit'
                }
            )),
            html.A(
                html.Img(
                    src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/"
                    "logo/new-branding/dash-logo-by-plotly-stripe-inverted.png"
                    ),
                href='https://plot.ly/products/dash/'
            ),
            html.A(
                html.Img(
                    src="/assets/help-button.png"
                    ),
                href='https://github.com/ogomezr/concept-drift-simulator'
            )
        ]),
    ]),
    html.Div(id='show-alg', className='row',
             children=[
                 html.Div(className='column2 left2',children=[
                 drc.NamedSliderNoPadding(
                     name='Show',
                     id='slider-show-alg',
                     min=1,
                     max=1000,
                     step=1,
                     marks={i: i for i in [0, 1000]},
                     value=1000,
                     disabled=True)]
                ),
                        html.Div(id='show',className='column2 right2', children=[
                            html.Button('<', id='button-<', disabled=True,
                                        style={'opacity': '0.2'}),
                            html.Button('>', id='button->', disabled=True,
                                        style={'opacity': '0.2'})
                        ])
                        
                 ]),

    dcc.Store(id='memory-seed1', storage_type='session'),
    dcc.Store(id='memory-seed2', storage_type='session'),
    html.Div(id='started', style={'display': 'none'}, children='0'),
    html.Div(id='reseted', style={'display': 'none'}, children='0'),
    html.Div(id='solution', style={'display': 'none'}),
    html.Div(id='predList', style={'display': 'none'}),
    html.Div(id='dataX', style={'display': 'none'}),
    html.Div(id='dataY', style={'display': 'none'}),
    html.Div(id='errorAcum', style={'display': 'none'}),
    html.Div(id='residuals', style={'display': 'none'}),
    html.Div(id='big', style={'display': 'none'}, children='300'),
    html.Div(id='small', style={'display': 'none'}, children='100'),
    html.Div(id='admissible', style={'display': 'none'}, children='0.1'),
    html.Div(id='threshold', style={'display': 'none'}, children='10'),
    html.Div(id='modelNames', style={'display': 'none'}),
    html.Div(id='showValue', style={'display': 'none'}),
    html.Div(id='showValue-<', style={'display': 'none'}),
    html.Div(id='showValue->', style={'display': 'none'}),
    html.Div(id='check-values', style={'display': 'none'}),
    visdcc.Run_js(id='javascript-button', run=""),
    visdcc.Run_js(id='javascript-finish', run=""),
    html.Div(id='interval', style={'display': 'none'}, children=[
        dcc.Interval(
            id='interval-component',
            interval=1*350, # in milliseconds
            n_intervals=0,
            disabled=True
        )]),
    html.Div(id='body', className='container scalable', children=[
        html.Div(className='row', children=[
            html.Div(
                id='div-graphs',
                children=dcc.Graph(
                    id='graph-Concept-Simulator',
                    style={'height': 'calc(100vh - 160px)',
                           'display': 'none'} 
                )
            ),
            # -----------------------------------------------------------------------------
            html.Div(
                id='options',
                className='three columns',
                style={
                    'min-width': '24.5%',
                    ##'max-height': 'calc(100vh - 85px)',
                    'max-height': 'calc(100vh - 160px)',
                    'overflow-y': 'auto',
                    'overflow-x': 'hidden'
                },
                children=[
                    visdcc.Run_js(id='javascript', run=""),
                    dcc.Tabs(id="tabs", value='init', children=[
                        dcc.Tab(label='Data init', value='init', 
                                style ={'color': '#329696'},
                                selected_style ={'color': '#329696'}),
                        dcc.Tab(label='Data change', value='change', 
                                style={'color': '#9660BB'},
                                selected_style={'color': '#9660BB'}),
                    ],style={
                        'padding': 20,
                        'margin': 5,
                        'borderRadius': 5,
                        'border': 'thin lightgrey solid'}),
                    drc.Card([
                        drc.NamedDropdown(
                            name='Dataset Initial',
                            id='dropdown-select-dataset',
                            options=[
                                {'label': 'Linear', 'value': 'straighLine'},
                                {'label': 'Polinomial  ax^3 + bx^2 + cx + d',
                                 'value': 'polinomial'},
                                {'label': 'Senoidal', 'value': 'senoidal'}
                            ],
                            clearable=False,
                            searchable=False,
                            value='straighLine'
                        ),

                        drc.NamedSlider(
                            name='Sample Size',
                            id='slider-dataset-sample-size',
                            min=200,
                            max=1000,
                            step=100,
                            marks={i: i for i in [200, 400, 600, 800, 1000]},
                            value=500
                        ),

                        drc.NamedSlider(
                            name='Noise Level',
                            id='slider-dataset-noise-level',
                            min=0,
                            max=5,
                            marks={i: i for i in [0, 1, 2, 3, 4, 5]},
                            step=0.2,
                            value=1,
                        ),
                        html.Div(id='linear-params', children=[
                            drc.NamedSlider(
                                name='Slope',
                                id='slider-slope',
                                min=-20,
                                max=20,
                                step=5,
                                marks={
                                    i: i for i in [-20, -15, -10, -5, 0, 5, 10, 15, 20]},
                                value=5
                            ),

                            drc.NamedSlider(
                                name='Axis Y',
                                id='slider-axis-y',
                                min=-50,
                                max=50,
                                step=5,
                                marks={i: i for i in [-50, -25, 0, 25, 50]},
                                value=0
                            ),
                        ]),
                        html.Div(id='pol-params', children=[
                            drc.NamedSlider(
                                name='a',
                                id='slider-a',
                                min=-2,
                                max=2,
                                step=0.2,
                                marks={i: i for i in [-2, -1, 0, 1, 2]},
                                value=0.8
                            ),

                            drc.NamedSlider(
                                name='b',
                                id='slider-b',
                                min=-10,
                                max=10,
                                step=0.2,
                                marks={i: i for i in [-10, -5, 0, 5, 10]},
                                value=-6
                            ),
                            drc.NamedSlider(
                                name='c',
                                id='slider-c',
                                min=-20,
                                max=20,
                                step=1,
                                marks={
                                    i: i for i in [-20, -15, -10, -5, 0, 5, 10, 15, 20]},
                                value=-10
                            ),

                            drc.NamedSlider(
                                name='d',
                                id='slider-d',
                                min=-10,
                                max=10,
                                step=1,
                                marks={i: i for i in [-10, -5, 0, 5, 10]},
                                value=10
                            ),
                        ]),
                        html.Div(id='senoidal-params', children=[
                            drc.NamedSlider(
                                name='Amplitude',
                                id='slider-amplitude',
                                min=0,
                                max=20,
                                step=20,
                                marks={i: i for i in [0, 5, 10, 15, 20]},
                                value=5
                            ),
                            drc.NamedSlider(
                                name='Angular frequency',
                                id='slider-angular',
                                min=1,
                                max=20,
                                step=1,
                                marks={i: i for i in [1, 5, 10, 15, 20]},
                                value=5
                            ),
                            drc.NamedSlider(
                                name='Phase',
                                id='slider-phase',
                                min=-10,
                                max=10,
                                step=20,
                                marks={i: i for i in [-10, -5, 0, 5, 10]},
                                value=0
                            ),
                        ]),

                    ], style={'color': '#329696'}, id='initData'),
                    # -----------------------------------------------------------------------------
                    drc.Card([
                        drc.NamedDropdown(
                            name='Dataset Change',
                            id='dropdown-select-dataset-second',
                            options=[
                                {'label': 'Linear', 'value': 'straighLine'},
                                {'label': 'Polinomial  ax^3 + bx^2 + cx + d',
                                 'value': 'polinomial'},
                                {'label': 'Senoidal', 'value': 'senoidal'}
                            ],
                            clearable=False,
                            searchable=False,
                            value='straighLine'
                        ),

                        drc.NamedSlider(
                            name='Sample Size',
                            id='slider-dataset-sample-size-second',
                            min=200,
                            max=1000,
                            step=100,
                            marks={i: i for i in [200, 400, 600, 800, 1000]},
                            value=500
                        ),

                        drc.NamedSlider(
                            name='Noise Level',
                            id='slider-dataset-noise-level-second',
                            min=0,
                            max=5,
                            marks={i: i for i in [0, 1, 2, 3, 4, 5]},
                            step=0.2,
                            value=1,
                        ),
                        html.Div(id='linear-params-second', children=[
                            drc.NamedSlider(
                                name='Slope',
                                id='slider-slope-second',
                                min=-20,
                                max=20,
                                step=5,
                                marks={
                                    i: i for i in [-20, -15, -10, -5, 0, 5, 10, 15, 20]},
                                value=10
                            ),

                            drc.NamedSlider(
                                name='Axis Y',
                                id='slider-axis-y-second',
                                min=-50,
                                max=50,
                                step=5,
                                marks={i: i for i in [-50, -25, 0, 25, 50]},
                                value=0
                            ),
                        ]),
                        html.Div(id='pol-params-second', children=[
                            drc.NamedSlider(
                                name='a',
                                id='slider-a-second',
                                min=-2,
                                max=2,
                                step=0.2,
                                marks={i: i for i in [-2, -1, 0, 1, 2]},
                                value=0.8
                            ),

                            drc.NamedSlider(
                                name='b',
                                id='slider-b-second',
                                min=-10,
                                max=10,
                                step=0.2,
                                marks={i: i for i in [-10, -5, 0, 5, 10]},
                                value=-6
                            ),
                            drc.NamedSlider(
                                name='c',
                                id='slider-c-second',
                                min=-20,
                                max=20,
                                step=1,
                                marks={
                                    i: i for i in [-20, -15, -10, -5, 0, 5, 10, 15, 20]},
                                value=-10
                            ),

                            drc.NamedSlider(
                                name='d',
                                id='slider-d-second',
                                min=-10,
                                max=10,
                                step=1,
                                marks={i: i for i in [-10, -5, 0, 5, 10]},
                                value=10
                            ),
                        ]),
                        html.Div(id='senoidal-params-second', children=[
                            drc.NamedSlider(
                                name='Amplitude',
                                id='slider-amplitude-second',
                                min=0,
                                max=20,
                                step=20,
                                marks={i: i for i in [0, 5, 10, 15, 20]},
                                value=5
                            ),
                            drc.NamedSlider(
                                name='Angular frequency',
                                id='slider-angular-second',
                                min=1,
                                max=20,
                                step=1,
                                marks={i: i for i in [1, 5, 10, 15, 20]},
                                value=5
                            ),
                            drc.NamedSlider(
                                name='Phase',
                                id='slider-phase-second',
                                min=-10,
                                max=10,
                                step=20,
                                marks={i: i for i in [-10, -5, 0, 5, 10]},
                                value=0
                            ),
                        ]),

                    ], style={'color': '#9660BB'}, id='changeData',)
                ]
            ),
        ]),
    ])
])


@app.callback(Output('linear-params', 'style'),
              [Input('dropdown-select-dataset', 'value')])
def toggle_container(toggle_value):
    if toggle_value == 'straighLine':
        return {'display': 'block'}
    if toggle_value == 'senoidal':
        return {'display': 'block'}
    return {'display': 'none'}


@app.callback(Output('linear-params-second', 'style'),
              [Input('dropdown-select-dataset-second', 'value')])
def toggle_container2(toggle_value):
    if toggle_value == 'straighLine':
        return {'display': 'block'}
    if toggle_value == 'senoidal':
        return {'display': 'block'}
    return {'display': 'none'}


@app.callback(Output('pol-params', 'style'),
              [Input('dropdown-select-dataset', 'value')])
def toggle_polinomial(toggle_value):
    if toggle_value == 'polinomial':
        return {'display': 'block'}
    return {'display': 'none'}


@app.callback(Output('pol-params-second', 'style'),
              [Input('dropdown-select-dataset-second', 'value')])
def toggle_polinomial2(toggle_value):
    if toggle_value == 'polinomial':
        return {'display': 'block'}
    return {'display': 'none'}


@app.callback(Output('senoidal-params', 'style'),
              [Input('dropdown-select-dataset', 'value')])
def toggle_senoidal(toggle_value):
    if toggle_value == 'senoidal':
        return {'display': 'block'}
    return {'display': 'none'}


@app.callback(Output('senoidal-params-second', 'style'),
              [Input('dropdown-select-dataset-second', 'value')])
def toggle_senoidal2(toggle_value):
    if toggle_value == 'senoidal':
        return {'display': 'block'}
    return {'display': 'none'}


@app.callback([Output('check-values', 'children'),
               Output('started', 'children')],
              [Input('button-start', 'n_clicks')],
              [State('started', 'children'),
               State('check-model','values')])
def disableFirst(n_clicks, started, check):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate()
    started = int(started) + 1
    return check,started


@app.callback([Output('big', 'children'),
               Output('small', 'children'),
               Output('admissible', 'children'),
               Output('threshold', 'children')
               ],
              [Input('slider-big-window', 'value'),
               Input('slider-small-window', 'value'),
               Input('slider-admissible', 'value'),
               Input('slider-threshold', 'value')])
def setSize(big, small, admissible, threshold):
    return big, small, admissible, threshold


@app.callback(Output('alg-params', 'children'),
              [Input('button-start', 'n_clicks')]
              )
def toggle_options(nclicks):
    if nclicks is None:
        raise dash.exceptions.PreventUpdate()
    
    return [
        
        dcc.Graph(
            id='graph-sup',
            style={'height': '45%', 'width': '100%'},
            figure={}
        ),

        dcc.Graph(
            id='graph-inf',
            figure={},
            style={'height': '45%'}
        ),

        html.Button(
            'Reset',
            id='button-reset',
            style={'height': '5%', 'margin-left': '100px'}
        ),
        
        html.Button(
            'Play',
            id='button-play',
            style={'height': '5%', 'margin-left': '20px'}
        ),
        
        html.Button(
            'Stop',
            id='button-stop',
            style={'height': '5%', 'margin-left': '20px', 'display':'none'}
        ),

    ]


@app.callback(Output('reseted', 'children'),
              [Input('button-reset', 'n_clicks')],
              [State('reseted', 'children')])
def toggle_reset(nclicks, reseted):
    if nclicks is None:
        raise dash.exceptions.PreventUpdate()
    reseted = int(reseted) + 1
    return reseted

@app.callback(Output('interval', 'children'),
              [Input('button-play', 'n_clicks'),
               Input('button-stop', 'n_clicks'),
               Input('reseted', 'children')],
              [State('slider-show-alg', 'max'),
               State('slider-show-alg', 'value')])
def playInterval(nplay, nstop, reset, maxShow, value):
    if nplay is None:
        raise dash.exceptions.PreventUpdate()
        
    tname = dash.callback_context.triggered[0]['prop_id']
    if tname == 'button-play.n_clicks':
        return [dcc.Interval(
                    id='interval-component',
                    interval=1*350, # in milliseconds
                    n_intervals=0,
                    max_intervals=maxShow/10,
                    disabled=False
                    )]
    elif tname =='button-stop.n_clicks':
        return [dcc.Interval(
                    id='interval-component',
                    interval=1*350, # in milliseconds
                    n_intervals=value/10,
                    disabled=True)]
    return [dcc.Interval(
            id='interval-component',
            interval=1*350, # in milliseconds
            n_intervals=-1,
            disabled=True)]

@app.callback(Output('javascript-finish', 'run'),
              [Input('interval-component', 'n_intervals')],
              [State('slider-show-alg', 'max')]
               )
def setPlayStyle(intervals, maxShow):   
    if intervals*10 == maxShow:
        return  '''
            document.getElementById("button-play").style.display = 'inline-block';
            document.getElementById("button-stop").style.display = 'none';
            document.getElementById("button-play").disabled = true;
            document.getElementById("button-play").style.opacity = '0.2';
            setTimeout(function(){                    
                document.getElementById("button-play").disabled = false;
                document.getElementById("button-play").style.opacity = '1';
                }, 1500);            
            '''
    return ''

@app.callback(Output('javascript-button', 'run'),              
              [Input('button-play', 'n_clicks'),
               Input('button-stop', 'n_clicks')
               ])
def disableButtonsJs(play,stop):
    if play is None:
        raise dash.exceptions.PreventUpdate()
      
    tname = dash.callback_context.triggered[0]['prop_id']
    if  tname == 'button-play.n_clicks':
        return  '''
                document.getElementById("button-play").style.display = 'none';
                document.getElementById("button-stop").style.display = 'inline-block';
                document.getElementById("button-stop").disabled = true;
                document.getElementById("button-stop").style.opacity = '0.2';
                setTimeout(function(){                    
                    document.getElementById("button-stop").disabled = false;
                    document.getElementById("button-stop").style.opacity = '1';
                    }, 1500);
                '''
    return  '''
            document.getElementById("button-play").style.display = 'inline-block';
            document.getElementById("button-stop").style.display = 'none';
            document.getElementById("button-play").disabled = true;
            document.getElementById("button-play").style.opacity = '0.2';
            setTimeout(function(){                    
                document.getElementById("button-play").disabled = false;
                document.getElementById("button-play").style.opacity = '1';
                }, 1500);            
            '''

@app.callback(Output('slider-show-alg', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setShowDisable(start, reset):
    if start == reset:
        return True
    return False

@app.callback(Output('dropdown-select-dataset', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataDisable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-dataset-sample-size', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataSizeDisable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-dataset-noise-level', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataNoiseDisable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-slope', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataSlopeDisable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-axis-y', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataAxisDisable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-a', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataADisable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-b', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataBDisable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-c', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataCDisable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-d', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataDDisable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-amplitude', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataAmplitudeDisable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-angular', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataAngularDisable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('linear-phase', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataPhaseDisable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('dropdown-select-dataset-second', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectData2Disable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-dataset-sample-size-second', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataSize2Disable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-dataset-noise-level-second', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataNoise2Disable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-slope-second', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataSlope2Disable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-axis-y-second', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataAxis2Disable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-a-second', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataA2Disable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-b-second', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataB2Disable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-c-second', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataC2Disable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-d-second', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataD2Disable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-amplitude-second', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataAmplitude2Disable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('slider-angular-second', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def dsetSelectDataAngular2Disable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('linear-phase-second', 'disabled'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setSelectDataPhase2Disable(start, reset):
    if start == reset:
        return False
    return True

@app.callback(Output('check-model', 'options'),
              [Input('started', 'children'),
               Input('reseted', 'children')])
def setModelOptionesDisable(start, reset):
    if start == reset:
        return [{'label': 'Lineal',
                 'value': 'lin',
                 'disabled': True},
                {'label': 'Polynomial',
                 'value': 'pol'},
                {'label': 'Tree Decision',
                 'value': 'tree'}]
    return [{'label': 'Lineal',
             'value': 'lin',
             'disabled': True},
            {'label': 'Polynomial',
             'value': 'pol',
             'disabled': True},
            {'label': 'Tree Decision',
             'value': 'tree',
             'disabled': True}]

@app.callback(Output('showValue-<', 'children'),
              [Input('button-<', 'n_clicks')],
              [State('slider-show-alg', 'value')]
              )
def valueUpdate1(button, value):
    if button is None:
        raise dash.exceptions.PreventUpdate()
    return value - 1


@app.callback(Output('showValue->', 'children'),
              [Input('button->', 'n_clicks')],
              [State('slider-show-alg', 'value')]
              )
def valueUpdate2(button, value):
    if button is None:
        raise dash.exceptions.PreventUpdate()
    return value + 1


@app.callback(Output('slider-show-alg', 'value'),
              [Input('showValue', 'children'),
               Input('showValue-<', 'children'),
               Input('showValue->', 'children'),
               Input('interval-component', 'n_intervals')
               ],
              [State('reseted','children'),
               State('started','children')]
              )
def valueUpdate(value1, value2, value3, interval, start, reset):
    tname = dash.callback_context.triggered[0]['prop_id']
    
    if tname == 'showValue.children':
        return value1
    elif tname == 'showValue-<.children':
        return value2
    elif tname == 'showValue->.children':
        return value3
    elif interval!=-1:
        return interval*10
    else:
        raise dash.exceptions.PreventUpdate()


@app.callback(Output('button-<', 'disabled'),
              [Input('slider-show-alg', 'value'),
               Input('reseted', 'children')],
              [State('slider-show-alg', 'max')])
def setButtonmDecreaseDisable(value, reset, maxValue):
    tname = dash.callback_context.triggered[0]['prop_id']
    if tname == 'reseted.children':
        return True
    if value == maxValue:
        return False
    if value == 1:
        return True
    return False

@app.callback(Output('button-<', 'style'),
              [Input('slider-show-alg', 'value'),
               Input('reseted', 'children')],
              [State('slider-show-alg', 'max')])
def setButtonmDecreaseStyle(value, reset, maxValue):
    tname = dash.callback_context.triggered[0]['prop_id']
    if tname == 'reseted.children':
        return {'opacity': '0.2'}
    if value == maxValue:
        return {'opacity': '1'}
    if value == 1:
        return {'opacity': '0.2'}
    return {'opacity': '1'}

@app.callback(Output('button->', 'disabled'),
              [Input('slider-show-alg', 'value'),
              Input('reseted', 'children')],
              [State('slider-show-alg', 'max')])
def setButtonIncreaseDisable(value, reset, maxValue):
    tname = dash.callback_context.triggered[0]['prop_id']
    if tname == 'reseted.children':
        return True
    if value == maxValue:
        return True
    if value == 1:
        return False
    return False

@app.callback(Output('button->', 'style'),
              [Input('slider-show-alg', 'value'),
               Input('reseted', 'children')],
              [State('slider-show-alg', 'max')])
def setButtonmIncreaseDisable(value, reset, maxValue):
    tname = dash.callback_context.triggered[0]['prop_id']
    if tname == 'reseted.children':
        return {'opacity': '0.2'}
    if value == maxValue:
        return {'opacity': '0.2'}
    if value == 1:
        return {'opacity': '1'}
    return {'opacity': '1'}

@app.callback([Output('initData', 'style'),
               Output('changeData', 'style')],
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'init':
        return {'padding': 20,
                'margin': 5,
                'borderRadius': 5,
                'border': 'thin lightgrey solid',
                'display':'block',
                'color': '#329696'},{'display':'none'}
    else:
        return {'display':'none'},{'padding': 20,
                'margin': 5,
                'borderRadius': 5,
                'border': 'thin lightgrey solid',
                'display':'block',
                'color': '#9660BB'}

@app.callback([Output('memory-seed1', 'data'),
               Output('memory-seed2', 'data'),
               Output('div-graphs', 'children')],
              [Input('dropdown-select-dataset', 'value'),
               Input('slider-dataset-sample-size', 'value'),
               Input('slider-dataset-noise-level', 'value'),
               Input('slider-slope', 'value'),
               Input('slider-axis-y', 'value'),
               Input('dropdown-select-dataset-second', 'value'),
               Input('slider-dataset-sample-size-second', 'value'),
               Input('slider-dataset-noise-level-second', 'value'),
               Input('slider-slope-second', 'value'),
               Input('slider-axis-y-second', 'value'),
               Input('slider-a', 'value'),
               Input('slider-b', 'value'),
               Input('slider-c', 'value'),
               Input('slider-d', 'value'),
               Input('slider-a-second', 'value'),
               Input('slider-b-second', 'value'),
               Input('slider-c-second', 'value'),
               Input('slider-d-second', 'value'),
               Input('slider-amplitude', 'value'),
               Input('slider-angular', 'value'),
               Input('slider-phase', 'value'),
               Input('slider-amplitude-second', 'value'),
               Input('slider-angular-second', 'value'),
               Input('slider-phase-second', 'value'),
               Input('reseted', 'children')],
              [State('big', 'children'),
               State('small', 'children'),
               State('admissible', 'children'),
               State('threshold', 'children')
               ])
def updateDataSet(dataset, nS, noise, slope, axisY,
                  dataset2, nS2, noise2, slope2, axisY2,
                  a, b, c, d, a2, b2, c2, d2,
                  amplitude, angular, phase,
                  amplitude2, angular2, phase2, reseted,
                  big, small, admissible, threshold):
    seed1 = np.random.randint(100)
    seed2 = np.random.randint(100)
    np.random.seed(seed1)
    X = np.random.rand(nS) * 10
    epsilon = np.random.normal(0, noise, nS)
    y = GenData.genData(dataset, X, slope, axisY, a, b, c, d,
                        amplitude, angular, phase) + epsilon

    np.random.seed(seed2)
    X2 = np.random.rand(nS2) * 10
    epsilon2 = np.random.normal(0, noise2, nS2)
    y2 = GenData.genData(dataset2, X2, slope2, axisY2, a2, b2, c2, d2,
                         amplitude2, angular2, phase2) + epsilon2

    bigSize = int(big)
    smallSize = int(small)
    admissibleP = float(admissible)
    thresholdP = int(threshold)

    prediction_figure = go.Figure(
        data=[go.Scatter(x=X, y=y, mode="markers", name="Dataset Initial",
                         line=dict(color='#329696')),
              go.Scatter(x=X2, y=y2, mode="markers", name="Dataset Change",
                         line=dict(color='#9660BB'))],
        layout=go.Layout(
            xaxis=dict(
                ticks='',
                showticklabels=True,
                showgrid=True,
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='black'
            ),
            yaxis=dict(
                ticks='',
                showticklabels=True,
                showgrid=True,
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='black'
            ),
            hovermode='closest',
            margin=dict(l=0, r=0, t=0, b=0),
            legend=go.layout.Legend(
                x=0,
                y=1,
                traceorder="normal",
                font=dict(
                    family="sans-serif",
                    size=12,
                    color="black"
                ),
                bgcolor="LightSteelBlue",
                bordercolor="Black",
                borderwidth=0.5
            ),
            title={
                'text': 'DATASET INITIAL - CHANGE',
                'y': 0.98,
                'x': 0.2,
                'font': {'family': "Courier New, monospace"}}
        )
    )
    return seed1, seed2,[
        html.Div(
            className='three columns',
            style={
                'min-width': '24.5%',
                'height': 'calc(100vh - 160px)',
                'margin-top': '5px',
                'user-select': 'none',
                '-moz-user-select': 'none',
                '-webkit-user-select': 'none',
                '-ms-user-select': 'none',
                'overflow-y': 'hidden',
                'overflow-x': 'hidden'
            },
            children=[
                html.Div(id='alg-params', style={'height': '100%', 'width': '100%'},
                         children=[
                             html.Div(id='buttons', style={'text-align':'center'}, children=[
                                 drc.Card([
                                     html.Button(
                                         'Start',
                                         id='button-start',
                                         style={'border':'1px solid #FF6847'}
                                         )
                                     ]),
                                 ]),
                             drc.Card([
                                    html.H6("Select Models : ",
                                            style={
                                                'text-decoration': 'none',
                                                'color': 'inherit'
                                            }
                                            ),
                                    dcc.Checklist(
                                        id='check-model',
                                        options=[
                                            {'label': 'Lineal', 'value': 'lin', 'disabled': True},
                                            {'label': 'Polynomial', 'value': 'pol'},
                                            {'label': 'Tree Decision', 'value': 'tree'}
                                        ],
                                        values=['lin', 'pol'],
                                        labelStyle={
                                            'display': 'inline-block',
                                            'margin-right': '1em'}
                                    )
                                ],id='models'),
                             drc.Card([
                                 html.H6("Page-Hinkley Parameters",
                                         style={
                                             'text-decoration': 'none',
                                             'color': 'inherit'}
                                         ),
                                 drc.NamedSlider(
                                     name='Admissible change',
                                     id='slider-admissible',
                                     min=0.1,
                                     max=2,
                                     step=0.1,
                                     marks={i: i for i in [0.1, 0.5, 1, 1.5, 2]},
                                     value=admissibleP
                                     ),
                                 drc.NamedSlider(
                                     name='Threshold',
                                     id='slider-threshold',
                                     min=10,
                                     max=100,
                                     step=1,
                                     marks={i: i for i in [10, 20, 50, 75, 100]},
                                     value=thresholdP
                                     )
                                 ]),
                             drc.Card([
                                 html.H6("Adaptative Algorithm Parameters",
                                         style={
                                             'text-decoration': 'none',
                                             'color': 'inherit'}
                                         ),
                                 drc.NamedSlider(
                                     name='Big window',
                                     id='slider-big-window',
                                     min=150,
                                     max=350,
                                     step=50,
                                     marks={i: i for i in [150, 200, 250, 300, 350]},
                                     value=bigSize
                                     ),
                                 drc.NamedSlider(
                                     name='Small window',
                                     id='slider-small-window',
                                     min=50,
                                     max=150,
                                     step=50,
                                     marks={i: i for i in [50, 100, 150]},
                                     value=smallSize
                                     )
                                 ])
                             ])
                ]),

        html.Div(
            className='six columns',
            style={'margin-top': '5px'},
            children=[
                dcc.Graph(
                    id='graph-main',
                    figure=prediction_figure,
                    style={'height': 'calc(100vh - 160px)'}
                )
            ]),

    ]

@app.callback([Output('solution', 'children'),
               Output('predList', 'children'),
               Output('errorAcum', 'children'),
               Output('residuals', 'children'),
               Output('dataX', 'children'),
               Output('dataY', 'children'),
               Output('modelNames', 'children'),
               Output('slider-show-alg', 'max'),
               Output('slider-show-alg', 'marks'),
               Output('showValue', 'children'),
               Output('javascript', 'run')
              ],
              [Input('started', 'children')],
              [State('memory-seed1', 'data'),
               State('memory-seed2', 'data'),
               State('dropdown-select-dataset', 'value'),
               State('slider-dataset-sample-size', 'value'),
               State('slider-dataset-noise-level', 'value'),
               State('slider-slope', 'value'),
               State('slider-axis-y', 'value'),
               State('dropdown-select-dataset-second', 'value'),
               State('slider-dataset-sample-size-second', 'value'),
               State('slider-dataset-noise-level-second', 'value'),
               State('slider-slope-second', 'value'),
               State('slider-axis-y-second', 'value'),
               State('slider-a', 'value'),
               State('slider-b', 'value'),
               State('slider-c', 'value'),
               State('slider-d', 'value'),
               State('slider-a-second', 'value'),
               State('slider-b-second', 'value'),
               State('slider-c-second', 'value'),
               State('slider-d-second', 'value'),
               State('slider-amplitude', 'value'),
               State('slider-angular', 'value'),
               State('slider-phase', 'value'),
               State('slider-amplitude-second', 'value'),
               State('slider-angular-second', 'value'),
               State('slider-phase-second', 'value'),
               State('check-values', 'children'),
               State('big', 'children'),
               State('small', 'children'),
               State('admissible', 'children'),
               State('threshold', 'children')
              ])
def startAlg(start,
             seed1, seed2,
             dataset, nS, noise, slope, axisY,
             dataset2, nS2, noise2, slope2, axisY2,
             a, b, c, d, a2, b2, c2, d2,
             amplitude, angular, phase,
             amplitude2, angular2, phase2,
             check, big, small, admissible, threshold):
    ##start_time = time()
    if start is None:
        raise dash.exceptions.PreventUpdate()
    if check is None:
        raise dash.exceptions.PreventUpdate()
    np.random.seed(seed1)
    X = np.random.rand(nS) * 10
    epsilon = np.random.normal(0, noise, nS)
    y = GenData.genData(dataset, X, slope, axisY, a, b, c, d,
                        amplitude, angular, phase) + epsilon

    X = X.tolist()
    y = y.tolist()

    bigSize = int(big)

    np.random.seed(seed1 + 1)
    Xbuild = np.random.rand(bigSize) * 10
    epsilon = np.random.normal(0, noise, bigSize)
    ybuild = GenData.genData(dataset, Xbuild, slope, axisY, a, b, c, d,
                             amplitude, angular, phase) + epsilon

    Xbuild = Xbuild.tolist()
    ybuild = ybuild.tolist()

    np.random.seed(seed2)
    X2 = np.random.rand(nS2) * 10

    epsilon2 = np.random.normal(0, noise2, nS2)
    y2 = GenData.genData(dataset2, X2, slope2, axisY2, a2, b2, c2, d2,
                         amplitude2, angular2, phase2) + epsilon2

    X2 = X2.tolist()
    y2 = y2.tolist()

    dataX = X + X2
    dataY = y + y2

    ##tart_time = time()

    smallSize = int(small)
    admissibleP = float(admissible)
    thresholdP = int(threshold)
    alg = DetectChangeAlg.DetectChangeAlg(
        bigSize,
        smallSize,
        Xbuild,
        ybuild,
        admissibleP,
        thresholdP,
        check)
    alg.addData(dataX, dataY)
    ##elapsed_time = time() - start_time



    ##start_time = time()
    solutionjson = '|'.join(map(str, alg.sol))
    predListjson = '|'.join(map(str, alg.predList))
    listModels = json.dumps(alg.modelNames)
    dataXjson = json.dumps(alg.xAllData)
    dataYjson = json.dumps(alg.yAllData)
    errorAcumJson = json.dumps(alg.ph.acummT)
    resJson = json.dumps(alg.error)

    ##elapsed_time = time() - start_time
    ##print("JSON: %.10f seconds." % elapsed_time)

    total = nS + nS2
    marks = {i: i for i in [total // 4, total // 2, total // 4 * 3, total]}
    return (solutionjson, predListjson, errorAcumJson, resJson, dataXjson, dataYjson,
            listModels, total, marks, total,
            '''
            document.scrollTop = 30;
            document.documentElement.scrollTop = 30;
            var myDiv = document.getElementById('options');
            myDiv.scrollTop = 0;
            document.getElementById("button-<").style.border = '1px solid #FF6847';
            document.getElementById("button-reset").style.border = '1px solid #FF6847';
            var slider = document.getElementById("slider-show-alg").getElementsByClassName("rc-slider-track")[0];
            slider.style.background= '#FF6847';
            setTimeout(function(){
               document.getElementById("button-<").style.border = '';
               document.getElementById("slider-show-alg").style.background= '';
               slider.style.background= '';
               document.getElementById("button-reset").style.border = '';
            }, 2000);
            ''')

@app.callback( Output('graph-main', 'figure'),
              [Input('slider-show-alg', 'value')],
              [State('solution', 'children'),
               State('predList', 'children'),
               State('dataX', 'children'),
               State('dataY', 'children'),
               State('modelNames', 'children'),
               State('big', 'children'),
               State('small', 'children'),
               State('admissible', 'children'),
               State('threshold', 'children')
               ])
def update_graph(
        value,
        solutionJson,
        predListJson,
        dataXJson,
        dataYJson,
        modelNames,
        big,
        small,
        admissible,
        threshold):
    if solutionJson is None:
        raise dash.exceptions.PreventUpdate()

    ##start = time()
    value = int(value)

    solution = solutionJson.split('|')
    solution = solution[value - 1]
    solution = solution.replace('(', ' ')
    solution = solution.replace(')', ' ')
    ini, fin, modelNumber = solution.split(',')
    ini, fin, modelNumber = int(ini), int(fin), int(modelNumber)
    predList = predListJson.split('|')
    predList = predList[modelNumber]
    predList = predList.split(',')
    predList[0] = predList[0].replace('[', ' ')
    predList[len(predList) - 1] = predList[len(predList) - 1].replace(']', ' ')
    rng = len(predList)
    for i in range(rng):
        predList[i] = float(predList[i])

    dataX = json.loads(dataXJson)

    dataY = json.loads(dataYJson)

    modelNamesArray = json.loads(modelNames)
    title = modelNamesArray[modelNumber] + ' Data N: ' + str(value) + '| Alg Bw ' + str(
        big) + ' Sw: ' + str(small) + '| PH- \u03BB: ' + str(threshold) + ' \u03C3: ' + str(admissible)

    r = np.arange(0, 10, 0.1)

    figure = go.Figure(
        data=[go.Scatter(x=dataX[ini:(fin - 1)], y=dataY[ini:(fin - 1)],
                         mode="markers", name="Old Data"),
              go.Scatter(x=dataX[fin - 1:fin],
                         y=dataY[fin - 1:fin],
                         mode="markers",
                         marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')),
                         name="Last Data",
                         line=dict(color='#ff7f0e')),
              go.Scatter(x=r, y=predList, name="Model", line=dict(color='red'))],
        layout=go.Layout(
            xaxis=dict(
                ticks='',
                showticklabels=True,
                showgrid=True,
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='black'

            ),
            yaxis=dict(
                ticks='',
                showticklabels=True,
                showgrid=True,
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='black'
            ),
            hovermode='closest',
            margin=dict(l=0, r=0, t=0, b=0),
            legend=go.layout.Legend(
                x=0,
                y=1,
                traceorder="normal",
                font=dict(
                    family="sans-serif",
                    size=12,
                    color="black"
                ),
                bgcolor="LightSteelBlue",
                bordercolor="Black",
                borderwidth=0.5
            ),
            title={
                'text': title,
                'y': 0.98,
                'x': 0.15,
                'font': {'family': "Courier New, monospace"}
            }
        )

    )
    ##elapsed_time = time() - start
    ##print("SHOW: %.10f seconds." % elapsed_time)
    return figure

@app.callback(Output('graph-sup', 'figure'),
              [Input('slider-show-alg', 'value')],
              [State('errorAcum', 'children')
               ])
def update_errorAcum(
        value,
        acumJson):
    if acumJson is None:
        raise dash.exceptions.PreventUpdate()

    errorAcum = json.loads(acumJson)
    figure = {"data": [{"type": "plot",
                         "mode": "markers",
                         "line": {"color": "#DF9C34"},
                         "y": errorAcum[0:value-1]}],
               "layout": {"title": {"text": "Acumulated Error PH"}}}

    return figure

@app.callback(Output('graph-inf', 'figure'),
              [Input('slider-show-alg', 'value')],
              [State('residuals', 'children')
               ])
def update_residuals(
        value,
        resdJson):
    if resdJson is None:
        raise dash.exceptions.PreventUpdate()

    residuals = json.loads(resdJson)
    figure = {"data": [{"type": "plot",
                         "mode": "markers",
                         "line": {"color": "#DF9C34"},
                         "y": residuals[0:value-1]}],
               "layout": {"title": {"text": "Acumulated Error PH"}}}

    return figure

external_css = [
    # Normalize the CSS
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
    # Fonts
    "https://fonts.googleapis.com/css?family=Open+Sans|Roboto",
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})

# Running the server
if __name__ == '__main__':
    app.run_server(debug=True)
