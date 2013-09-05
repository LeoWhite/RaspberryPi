raspivid -o - -w 960 -h 540 -t 999999999  |  vlc -v -I "dummy" stream:///dev/stdin  :sout="#std{access=livehttp{seglen=10,delsegs=true,numsegs=5, index=/var/www/streaming/stream.m3u8, index-url=http://109.145.254.207:8091/streaming/stream-########.ts}, mux=ts{use-key-frames}, dst=/var/www/streaming/stream-########.ts}" :demux=h264

