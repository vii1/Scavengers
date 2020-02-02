program Scavengers;
const
    LINEAS_DEBUG = 1;

global
    nave_fpg;
    deltatime=0;
    focal=400;
    color_debug1;
private
    prev_t=0;
begin
    set_mode(m640x480);
    set_fps(60,0);
    vsync=1;
    write_int(0,0,0,0,&fps);
    write(0,0,10,0,"focal = ");
    write_int(0,48,10,0,&focal);
    nave_fpg = load_fpg("vii\scavngrs\objetos\prota\prota.fpg");
    if(LINEAS_DEBUG)
        color_debug1 = find_color(63,0,63);
    end
    nave();
    priority=100;
    loop
        if(key(_q)) focal-=deltatime; end
        if(key(_e)) focal+=deltatime; end
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
    linea;
    col;
begin
    if(LINEAS_DEBUG)
        linea=draw(1,color_debug1,15,0,0,0,0,0);
    end
    write(0,0,20,0,"z = ");
    write_int(0,32,20,0,&z);
    priority = 10;
    resolution = 100;
    x=32000;
    y=24000;
    from i=0 to 13;
        capas[i]=nave_capa(i);
    end
    z = 0;
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
        if(key(_r)) z -= deltatime; end
        if(key(_f)) z += deltatime; end
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
        if(LINEAS_DEBUG)
            move_draw(linea,color_debug1,15,x/100,y/100,calc_x(x,z)/100,calc_y(y,z)/100);
        end
        frame;
        vx = vx * friction / 100;
        vy = vy * friction / 100;
    end
end

process nave_capa(capa)
begin
    priority = father.priority - 1;
    resolution = 100;
    file = nave_fpg;
    graph = capa+1;
    loop
        z = father.z-capa;
        size = calc_size(z);
        x=calc_x(father.x,z);
        y=calc_y(father.y,z);
        frame;
    end
end

function calc_size(z)
begin
    return(100*focal/(z+focal));
end

function calc_x(x,z)
begin
    return((x-32000)*focal/(z+focal)+32000);
end

function calc_y(y,z)
begin
    return((y-48000)*focal/(z+focal)+48000);
end