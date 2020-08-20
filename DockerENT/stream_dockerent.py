"""UI for DockerENT"""
import streamlit as st
import docker
st.title("This is DockerENT")

docker_client = docker.from_env()

docker_list = docker_client.containers.list()
docker_list.insert(0, 'All')

docker_nw_list = docker_client.networks.list()
docker_nw_list.insert(0, 'All')

scan_dockers = st.checkbox('Scan dockers')
scan_docker_networks = st.checkbox('Scan docker networks')

if scan_dockers:
    docker_scan_options = st.selectbox(
        'Pick a single docker or all to start.',
        docker_list
    )
if scan_docker_networks:
    docker_nw_options = st.selectbox(
        'Pick a single network or all to start',
        docker_nw_list
    )
if scan_dockers or scan_docker_networks:
    start_scan = st.button('Start Scan')

