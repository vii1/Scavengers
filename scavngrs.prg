program Scavengers;
const
global
    persp = 500;
    nave_fpg;
    deltatime=0;
private
    prev_t=0;
begin
    set_mode(m640x480);
    set_fps(60,0);
    vsync=1;
    write_int(0,0,0,0,&fps);
    write(0,0,10,0,"persp = ");
    write_int(0,64,10,0,&persp);
    nave_fpg = load_fpg("vii\scavngrs\objetos\prota\prota.fpg");
    nave();
    priority=100;
    loop
        if(key(_q)) persp-=deltatime; end
        if(key(_e)) persp+=deltatime; end
        prev_t=timer;
        frame;
        deltatime=timer-prev_t;
    end
end

process nave()
private
    capas[13];
    i;
    vx=0, vy=0;
    power=200;
    accx=0, accy=0;
    maxv = 1000;
    friction = 85;
begin
    priority = 10;
    resolution = 100;
    x=32000;
    y=24000;
    from i=0 to 13;
        capas[i]=nave_capa(i);
    end
    loop
        if(key(_left) && !key(_right))
            if(accx > 0) accx = 0;
            else accx -= power * deltatime / 100;
            end
        end
        if(key(_right) && !key(_left))
            if(accx < 0) accx = 0;
            else accx += power * deltatime / 100;
            end
        end
        if(!key(_right) && !key(_left))
            accx = 0;
        end
        if(key(_up) && !key(_down))
            if(accy > 0) accy = 0;
            else accy -= power * deltatime / 100;
            end
        end
        if(key(_down) && !key(_up))
            if(accy < 0) accy = 0;
            else accy += power * deltatime / 100;
            end
        end
        if(!key(_up) && !key(_down))
            accy = 0;
        end
        vx += accx;
        vy += accy;
        if(vx > maxv) vx= maxv; end
        if(vx < -maxv) vx = -maxv; end
        if(vy > maxv) vy= maxv; end
        if(vy < -maxv) vy = -maxv; end
        x += vx;
        y += vy;
        if(x<2500) x=2500; vx=0; accx=0; end
        if(y<2500) y=2500; vy=0; accy=0; end
        if(x>61500) x=61500; vx=0; accx=0; end
        if(y>45500) y=45500; vy=0; accy=0; end
        frame;
        vx = vx * friction / 100;
        vy = vy * friction / 100;
    end
end

process nave_capa(capa)
private
    px, py;
begin
    priority = father.priority - 1;
    resolution = 100;
    file = nave_fpg;
    graph = capa+1;
    z = 100 - capa;
    loop
        px = (father.x-32000)*capa*persp/240000;
        py = (father.y-48000)*capa*persp/240000;
        x=father.x+px;
        y=father.y+py;
        angle = father.angle;
        frame;
    end
end
