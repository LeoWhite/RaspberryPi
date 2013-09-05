raspivid -fps 10 -hf -vf -w 960 -h 540 -o - -t 0 |cvlc --network-caching=0 stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8554}' :demux=h264
