import json
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'HTML_output_plugin'


def write(queue, filename='out.html'):
    """Plugin to create beautiful html file for output.

    :param queue:
    :param filename:
    :return:
    """
    _log.info('Writing to {} ...'.format(filename))

    nodes = []
    edges = []

    report = {}
    while not queue.empty():
        result = queue.get()
        for key in result.keys():
            if key in report.keys():
                report[key].append(result[key])
            else:
                report[key] = []
                report[key].append(result[key])

    """
    After processing the list would look something like this.
    {
      "3911e81b25": [
        {
          "sample": {
            "status": "good"
          }
        }
      ]
    }
    """
    group = -1
    for docker_node in report.keys():
        group += 1
        nodes.append(
            {
                'id': docker_node,
                'shape': 'image',
                'image': 'https://www.docker.com/sites/default/files/d8/2019'
                         '-07/Moby-logo.png',
                'label': docker_node,
                'pluginname': docker_node,
                'data': 'This is docker node',
                'labelHighlightBold': True
            }
        )
        for plugin_node in report[docker_node]:
            for plugin_data_node in plugin_node.keys():
                node_id = 'plugin_' + plugin_data_node + '_' + docker_node
                nodes.append(
                    {
                        'id': node_id,
                        'shape': 'dot',
                        'label': plugin_data_node,
                        'pluginname': plugin_data_node,
                        'data': 'This is plugin node',
                        'labelHighlightBold': True
                    }
                )

                edges.append(
                    {
                        'from': docker_node,
                        'to': node_id,
                        'length': 200
                    }
                )

                for cmd_node in plugin_node[plugin_data_node].keys():
                    child_node_id = docker_node + '_' + cmd_node
                    nodes.append(
                        {
                            'id': child_node_id,
                            'shape': 'dot',
                            'label': cmd_node,
                            'pluginname': cmd_node,
                            'data': plugin_node[plugin_data_node][cmd_node][
                                'results'],
                            'labelHighlightBold': True,
                            'group': group
                        }
                    )
                    edges.append(
                        {
                            'from': node_id,
                            'to': child_node_id,
                            'value': 5,
                            'length': 100
                        }
                    )

    data = html_page_data.format(json.dumps(nodes, indent=2), json.dumps(
        edges, indent=2))

    with open(filename, 'w+') as file:
        file.write(html_page_pre_data + data + html_page_post_data)


html_page_pre_data = """
<!doctype html>
<html>

<head>
    <title>DockerENT | Analysis Report</title>
    <style type="text/css">
        body {
            font: 10pt arial;
        }

        #dockernetwork {
            height: 1000px;
            border: 1px solid lightgray;
            background-color: #333333;
        }

        .Modal {
            display: block;
            position: fixed;
            left: 0;
            top: 0;
            z-index: 9999;
            width: 100%;
            height: 100%;
            padding-top: 100px;
            background-color: black;
            background-color: rgba(0, 0, 0, 0.4);
            -webkit-transition: 0.5s;
            overflow: auto;
            transition: all 0.3s linear;
        }

        .Modal-content {
            background-color: #fefefe;
            margin: auto;
            padding: 20px;
            border-radius: 4px;
            max-width: 500px;
            height: 450px;
        }

        .ModalOpen {
            overflow: hidden;
        }

        .is-hidden {
            display: none;
        }

        .is-visuallyHidden {
            opacity: 0;
        }

        .Close {
            color: #aaaaaa;
            float: right;
            font-size: 16px;
        }

        .Close:focus {
            color: #000;
            text-decoration: none;
            cursor: pointer;
        }

        .is-blurred {
            filter: blur(2px);
            -webkit-filter: blur(2px);
        }


        body {
            background-color: #FCFCFC;
        }


        .cover {
            height: 100%;
            width: 100%;
            position: absolute;
            z-index: 1;
        }

        /*
        CSS for pop-up
        */
        body {
            background-color: #FCFCFC;
        }

        .cover {
            height: 100%;
            width: 100%;
            position: absolute;
            z-index: 1;
        }

        .blur-in {
            -webkit-animation: blur 2s forwards;
            -moz-animation: blur 2s forwards;
            -o-animation: blur 2s forwards;
            animation: blur 2s forwards;
        }

        .blur-out {
            -webkit-animation: blur-out 2s forwards;
            -moz-animation: blur-out 2s forwards;
            -o-animation: blur-out 2s forwards;
            animation: blur-out 2s forwards;
        }

        @-webkit-keyframes blur {
            0% {
                -webkit-filter: blur(0px);
                -moz-filter: blur(0px);
                -o-filter: blur(0px);
                -ms-filter: blur(0px);
                filter: blur(0px);
            }

            100% {
                -webkit-filter: blur(4px);
                -moz-filter: blur(4px);
                -o-filter: blur(4px);
                -ms-filter: blur(4px);
                filter: blur(4px);
            }
        }

        @-moz-keyframes blur {
            0% {
                -webkit-filter: blur(0px);
                -moz-filter: blur(0px);
                -o-filter: blur(0px);
                -ms-filter: blur(0px);
                filter: blur(0px);
            }

            100% {
                -webkit-filter: blur(4px);
                -moz-filter: blur(4px);
                -o-filter: blur(4px);
                -ms-filter: blur(4px);
                filter: blur(4px);
            }
        }

        @-o-keyframes blur {
            0% {
                -webkit-filter: blur(0px);
                -moz-filter: blur(0px);
                -o-filter: blur(0px);
                -ms-filter: blur(0px);
                filter: blur(0px);
            }

            100% {
                -webkit-filter: blur(4px);
                -moz-filter: blur(4px);
                -o-filter: blur(4px);
                -ms-filter: blur(4px);
                filter: blur(4px);
            }
        }

        @keyframes blur {
            0% {
                -webkit-filter: blur(0px);
                -moz-filter: blur(0px);
                -o-filter: blur(0px);
                -ms-filter: blur(0px);
                filter: blur(0px);
            }

            100% {
                -webkit-filter: blur(4px);
                -moz-filter: blur(4px);
                -o-filter: blur(4px);
                -ms-filter: blur(4px);
                filter: blur(4px);
            }
        }

        @-webkit-keyframes blur-out {
            0% {
                -webkit-filter: blur(4px);
                -moz-filter: blur(4px);
                -o-filter: blur(4px);
                -ms-filter: blur(4px);
                filter: blur(4px);
            }

            100% {
                -webkit-filter: blur(0px);
                -moz-filter: blur(0px);
                -o-filter: blur(0px);
                -ms-filter: blur(0px);
                filter: blur(0px);
            }
        }

        @-moz-keyframes blur-out {
            0% {
                -webkit-filter: blur(4px);
                -moz-filter: blur(4px);
                -o-filter: blur(4px);
                -ms-filter: blur(4px);
                filter: blur(4px);
            }

            100% {
                -webkit-filter: blur(0px);
                -moz-filter: blur(0px);
                -o-filter: blur(0px);
                -ms-filter: blur(0px);
                filter: blur(0px);
            }
        }

        @-o-keyframes blur-out {
            0% {
                -webkit-filter: blur(4px);
                -moz-filter: blur(4px);
                -o-filter: blur(4px);
                -ms-filter: blur(4px);
                filter: blur(4px);
            }

            100% {
                -webkit-filter: blur(0px);
                -moz-filter: blur(0px);
                -o-filter: blur(0px);
                -ms-filter: blur(0px);
                filter: blur(0px);
            }
        }

        @keyframes blur-out {
            0% {
                -webkit-filter: blur(4px);
                -moz-filter: blur(4px);
                -o-filter: blur(4px);
                -ms-filter: blur(4px);
                filter: blur(4px);
            }

            100% {
                -webkit-filter: blur(0px);
                -moz-filter: blur(0px);
                -o-filter: blur(0px);
                -ms-filter: blur(0px);
                filter: blur(0px);
            }
        }

        .content {
            width: 650px;
            margin: 0 auto;
            padding-top: 100px;
        }

        span {
            color: dimgray;
        }

        .pop-up {
            position: fixed;
            margin: 5% auto;
            left: 0;
            right: 0;
            z-index: 2;
        }

        .box {
            background-color: whitesmoke;
            text-align: center;
            margin-left: auto;
            margin-right: auto;
            margin-top: 10%;
            position: relative;
            -webkit-box-shadow: 0px 4px 6px 0px rgba(0, 0, 0, 0.1);
            -moz-box-shadow: 0px 4px 6px 0px rgba(0, 0, 0, 0.1);
            box-shadow: 0px 4px 6px 0px rgba(0, 0, 0, 0.1);
        }

        .button {
            background-color: #2496ed;
            margin-bottom: 33px;
            align-self: center;
        }

        .button:hover {
            background-color: #7CCF29;
            -webkit-box-shadow: 0px 4px 6px 0px rgba(0, 0, 0, 0.1);
            -moz-box-shadow: 0px 4px 6px 0px rgba(0, 0, 0, 0.1);
            box-shadow: 0px 4px 6px 0px rgba(0, 0, 0, 0.1);
        }

        .close-button {
            transition: all 0.5s ease;
            position: relative;
            background-color: #2496ed;
            padding: 1.5px 7px;
            left: 0;
            margin-left: -10px;
            margin-top: -9px;
            border-radius: 50%;
            border: 2px solid #fff;
            color: white;
            -webkit-box-shadow: -4px -2px 6px 0px rgba(0, 0, 0, 0.1);
            -moz-box-shadow: -4px -2px 6px 0px rgba(0, 0, 0, 0.1);
            box-shadow: -3px 1px 6px 0px rgba(0, 0, 0, 0.1);
        }

        .close-button:hover {
            background-color: #07416d;
            color: #fff;
        }

        h3 {
            text-align: center;
            padding-top: 15px;
            padding-bottom: 15px;
            color: #fff;
            background-color: #2496ed;
        }

        p {
            padding: 20px 65px 10px 65px;
            color: dimgray;
        }

        h1 {
            color: dimgray;
            font-family: Garamond, Baskerville, "Baskerville Old Face", "Hoefler Text", "Times New Roman", serif;
        }
    </style>

    <script type="text/javascript" src="https://visjs.github.io/vis-network/standalone/umd/vis-network.min.js"></script>
    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
        integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">

    <!-- Optional theme -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css"
        integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">

    <!-- Latest compiled and minified JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"
        integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa"
        crossorigin="anonymous"></script>

    <script type="text/javascript">

        // Get the modal
        var modal = document.getElementById('myModal');

        // Get the main container and the body
        var body = document.getElementsByTagName('body');
        var container = document.getElementById('myContainer');

        // When the user clicks anywhere outside of the modal, close it
        window.onclick = function (event) {
            if (event.target == modal) {
                modal.className = "Modal is-hidden";
                body.className = "";
                container.className = "MainContainer";
                container.parentElement.className = "";
            }
        }


        var nodes = null;
        var edges = null;
        var network = null;

        // Called when the Visualization API is loaded.
        function draw() {
            // create people.
            // value corresponds with the age of the person
"""
html_page_data = """
            nodes = new vis.DataSet({});
            edges = new vis.DataSet({});
"""

html_page_post_data = """            
            // create a network
            var container = document.getElementById('dockernetwork');
            var data = {
                nodes: nodes,
                edges: edges
            };
            var options = {
                nodes: {
                    borderWidth: 4,
                    size: 50,
                    color: {
                        border: '#222222',
                        background: '#666666'
                    },
                    font: { color: '#eeeeee' }
                },
                edges: {
                    color: 'lightgray'
                }
            };


            network = new vis.Network(container, data, options);
            network.on('click', function (properties) {
                var ids = properties.nodes;
                var clickedNode = nodes.get(ids)[0];
                console.log('clicked nodes:', clickedNode);
                // Open the modal
                var modal = document.getElementById('myModal');
                var pluginname = document.getElementById('pluginname')
                pluginname.innerText = clickedNode.pluginname;

                var plugindata = document.getElementById("plugindata");
                plugindata.innerText = clickedNode.data;

                modal.className = "Modal is-visuallyHidden";
                setTimeout(function () {
                    container.className = "MainContainer is-blurred";
                    modal.className = "Modal";
                }, 100);
                container.parentElement.className = "ModalOpen";

                // Close the modal
                var btnClose = document.getElementById("closeModal");
                btnClose.onclick = function () {
                    modal.className = "Modal is-hidden is-visuallyHidden";
                    body.className = "";
                    container.className = "MainContainer";
                    container.parentElement.className = "";
                }

                // When the user clicks anywhere outside of the modal, close it
                window.onclick = function (event) {
                    if (event.target == modal) {
                        modal.className = "Modal is-hidden";
                        body.className = "";
                        container.className = "MainContainer";
                        container.parentElement.className = "";
                    }
                }
            });
        }
    </script>

</head>

<body onload="draw()">
    <div id="myModal" class="Modal is-hidden is-visuallyHidden">
        <!-- Modal content -->
        <div class="Modal-content">
            <a href="#" class="close-button" id="closeModal">&#10006;</a>
            <h3 id="pluginname">lorem ipsum</h3>
            <p id="plugindata"></p>
        </div>
    </div>

    <nav class="navbar navbar-inverse navbar-fixed-top">
        <div class="container">
            <div class="navbar-header">
                <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar"
                    aria-expanded="false" aria-controls="navbar">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="#">DockerENT</a>
            </div>
            <!--/.navbar-collapse -->
        </div>
    </nav>

    <!-- Main jumbotron for a primary marketing message or call to action -->
    <div class="jumbotron">
        <div class="container">
            <h2></h2>
            <p></p>
            <!-- <p><a class="btn btn-primary btn-lg" href="#" role="button">Learn more &raquo;</a></p> -->
        </div>
    </div>

    <!-- Example row of columns -->
    <div class="row">
        <div class="col-1" id="dockernetwork">
            <h2></h2>
            <p></p>
            <p><a class="btn btn-default" href="#" role="button">View details &raquo;</a></p>
        </div>
    </div>


    <hr>
    <footer>
        <center>
            <p>&copy; DockerENT </p>
        </center>
    </footer>
</body>
</html>

"""
