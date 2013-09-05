raspivid -hf -vf -w 960 -h 540 -o - -t 0 |cvlc --network-caching=0 -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/}' :demux=h264
