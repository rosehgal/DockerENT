<p align="center">
  <img width="300" height="300" src="static/logo.png">
</p>

# DockerENT

DockerENT is activ**E** ru**N**time application scanning **T**ool (RAST) which is pluggable and written in python. It comes with CLI application and Web Interface written with [StreamLit](https://www.streamlit.io/).

DockerENT is designed keeping in mind that during deployments there weak configurations which are implemented and leads to severe consequenes. This application connects with running containers in the system and fetches the list of malicious runtime configurtions and generates a report. If invoved through CLI it can create `JSON` and `HTML` report. If invoked through Stream lit web interface, it can display the scan and audit report in the UI itself.

### How to Run
```bash
# Download and setup
git clone https://github.com/r0hi7/DockerENT.git
cd DockerENT
make venv
source venv/bin/activate

# Run
python -m DockerENT --help 
usage: Find the vulnerabilities hidden in your running container(s).
       [-h] [-d [DOCKER_CONTAINER]] [-p [DOCKER_PLUGINS]]
       [-d-nw [DOCKER_NETWORK]] [-p-nw [DOCKER_NW_PLUGINS]] [-w]
       [-n [PROCESS_COUNT]] [-a] [-o [OUTPUT]]

optional arguments:
  -h, --help            show this help message and exit
  -w, --web-app         Run DockerENT in WebApp mode. If this parameter is
                        enabled, other command line flags will be ignored.
  -n [PROCESS_COUNT], --process [PROCESS_COUNT]
                        Run scans in parallel (Process pool count).
  -a, --audit           Flag to check weather to audit results or not.

  -d [DOCKER_CONTAINER], --docker [DOCKER_CONTAINER]
                        Run scan against the running container.
  -p [DOCKER_PLUGINS], --plugins [DOCKER_PLUGINS]
                        Run scan with only specified plugins.
  -p-nw [DOCKER_NW_PLUGINS], --nw-plugins [DOCKER_NW_PLUGINS]
                        Run scan with only specified plugins.

  -d-nw [DOCKER_NETWORK], --docker-network [DOCKER_NETWORK]
                        Run scan against running docker-network.

  -o [OUTPUT], --output [OUTPUT]
                        Output plugin to write data to.
```



