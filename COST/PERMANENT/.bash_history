r.in.gdal cost.tif cost
r.in.gdal cost.tif out=cost
r.cost --h
r.cost cost start_coord=49.117355,55.789082 stop_coord=49.117509,55.788798 out=path
r.cost cost start_coord=49.117355,55.789082 stop_coord=49.117509,55.788798 output=path
g.region --h
g.region w=49.117255 n=55.799082  e=49.117609 s=55.787798 -p
r.cost cost start_coord=49.117355,55.789082 stop_coord=49.117509,55.788798 output=path
g.gui
v.import input=/home/klsvd/laboro/OSM/Kazan2019/data/highway-line.shp layer=highway-line output=highway_line
v.out.ascii path
v.out.ascii path --help
v.out.ascii path format=standard
v.to.points
v.to.points input=path@PERMANENT output=p use=vertex
v.out.ascii p
v.out.ascii p sep=,
v.generalize
v.generalize input=path@PERMANENT output=ps method=douglas threshold=0.0001 look_ahead=3
v.generalize input=path@PERMANENT output=ps method=douglas threshold=0.00001 look_ahead=3
v.generalize --overwrite input=path@PERMANENT output=ps method=douglas threshold=0.00001 look_ahead=3
v.generalize --overwrite input=path@PERMANENT output=ps method=douglas threshold=0.00005 look_ahead=3
r.null cost setnull=0
r.report cost un=c
g.region rast=cost
r.null cost setnull=0.0001
r.null cost setnull=0
r.report cost un=c
g.region w=49.117255 n=55.799082  e=49.117609 s=55.787798 -p
r.cost --h
r.cost cost null_cost=0.0001 start_coord=49.117355,55.789082 stop_coord=49.117509,55.788798 output=path --o
g.gui
r.drain --h
r.drain path out=p start_coord=49.117509,55.788798
r.cost cost null_cost=0.000001 start_coord=49.117355,55.789082 stop_coord=49.117509,55.788798 output=path --o
r.drain path out=p start_coord=49.117509,55.788798 --o
r.to.vect p out=p
r.to.vect p out=p type=line
r.buffer cost --h
r.buffer cost out=cost_buf dist=5 un=meters
r.buffer cost out=cost_buf dist=3 un=meters
r.buffer cost out=cost_buf dist=3 un=meters --o
r.mapcalc "cost_buf = cost_buf > 0" --o
r.cost cost_buf null_cost=0.000001 start_coord=49.117355,55.789082 stop_coord=49.117509,55.788798 output=path --o
r.drain path out=p start_coord=49.117509,55.788798 --o
r.to.vect p out=p type=line
r.to.vect p out=p type=line --o
g.region rast=cost
r.buffer cost out=cost_buf dist=3 un=meters --o
g.region w=49.217255 n=55.899082  e=49.117609 s=55.687798 -p
r.cost cost_buf null_cost=0.000001 start_coord=49.117355,55.789082 stop_coord=49.117509,55.788798 output=path --o
g.region w=49.117255 n=55.799082  e=49.119609 s=55.787798 -p
r.cost cost_buf null_cost=0.000001 start_coord=49.117355,55.789082 stop_coord=49.117509,55.788798 output=path --o
r.drain path out=p start_coord=49.117509,55.788798 --o
r.to.vect p out=p type=line --o
g.region rast=cost
r.mapcalc "cost_buf = cost_buf > 0" --o
r.buffer cost out=cost_buf dist=2 un=meters --o
r.mapcalc "cost_buf = cost_buf > 0" --o
g.region -p
pwd
ls
#v.to.rast highway_line out=roads 
g.region raast=cost
g.region rast=cost
v.to.rast highway_line out=roads use=val val=0
r.report cost un=c
r.report road un=c
r.report roads un=c
r.patch cost,roads out=cost_with_roads
r.patch roads,cost out=cost_with_roads --o
r.cost --h
r.drain --h
r.to.vect --h
g.list rast
r.to.vect input=path output=path type='line'
g.list rast
g.remove rast pat="p*"
g.remove rast pat="p*" -f
g.list vect
g.remove vect pat="p*" -f
g.list rast
GRASS_PAGER=cat
g.list rast
r.patch roads,cost_buf out=cost_with_roads --o
g.region rast=cost
r.patch roads,cost_buf out=cost_with_roads --o
r.info roads
r.info cost_buf
r.info cost_with_roads
v.info nodes
v.to.points --h
g.region -p
r.info cost
g.list rast
GRASS_PAGER=cat
g.list rast
g.remove rast name='roads'
g.remove rast name='roads' -f
g.remove rast name='path' -f 
g.remove rast name='cum)cost' -f 
g.remove rast name='cum_cost' -f 
g.list vect
g.remove vect pat="*" -f
