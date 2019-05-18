# encoding: utf-8

import sys
import os
import subprocess


class GRASS():
    def __init__(self, gisdbase, location, mapset='PERMANENT'):

        # query GRASS 7 itself for its GISBASE
        startcmd = ['grass', '--config', 'path']
        
        p = subprocess.Popen(startcmd, shell=False,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
            sys.exit(-1)
        gisbase = out.strip('\n\r')
        
        self.gisbase = os.environ['GISBASE'] = gisbase
        self.gisdbase =  gisdbase

        self.location = location
        self.mapset =  mapset

        # Пока не обновлены пути, импортировать GRASS не удастся
        sys.path.append(os.path.join(os.environ['GISBASE'], "etc", "python"))
        import grass.script as grass
        import grass.script.array as garray
        import grass.script.setup as gsetup
        

        self.grass = grass
        self.garray = garray
        self.gsetup = gsetup

        # Активируем GRASS
        self.gsetup.init(self.gisbase,
            self.gisdbase, self.location, self.mapset)
        
    

    def find_path(self, xstart, ystart, xfin, yfin):
        """
        r.buffer cost out=cost_buf dist=3 un=meters --o
        r.mapcalc "cost_buf = cost_buf > 0" --o
        
        g.region w=49.117255 n=55.799082  e=49.117609 s=55.787798 -p
        r.cost cost null_cost=0.0001 start_coord=49.117355,55.789082 stop_coord=49.117509,55.788798 output=path --o
        r.drain path out=p start_coord=49.117509,55.788798 --o
        """
        cost_map = 'cost_with_roads'
        cum_cost = 'cum_cost'
        path = 'path'
        path_smooth = 'ps'
        nodes = 'nodes'
        
        xmin, xmax = min(xstart, xfin), max(xstart, xfin)
        ymin, ymax = min(ystart, yfin), max(ystart, yfin)
        
        bbox_buf = 0.001
        self.grass.run_command('g.region', s=ymin-bbox_buf, n=ymax+bbox_buf, w=xmin-bbox_buf, e=xmax+bbox_buf)
        start = "%s,%s" % (xstart, ystart)
        fin = "%s,%s" % (xfin, yfin)
        self.grass.run_command('r.cost', input=cost_map, null_cost=0.0001, 
                              start_coordinates=start, stop_coordinates=fin,
                              output=cum_cost, overwrite=True
                              )
        self.grass.run_command('r.drain', input=cum_cost, output=path, start_coordinates=fin, overwrite=True)# Именно fin, не перепутано!
        self.grass.run_command('r.to.vect', input=path, output=path, type='line', overwrite=True)
        self.grass.run_command('v.generalize', 
                               input=path, output=path_smooth, 
                               method='douglas', threshold=0.00003, look_ahead=3, overwrite=True)
        self.grass.run_command('v.to.points', input=path_smooth, output=nodes, use='vertex', overwrite=True)     
        
        nodes = self.grass.read_command('v.out.ascii', input=nodes, overwrite=True)       
        nodes = nodes.strip()
        
        coords = []
        for line in nodes.split():
            x,y,_ = line.split('|')
            coords.append((float(x), float(y)))

        
        return coords

