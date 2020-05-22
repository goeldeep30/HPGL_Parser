import sys
import json

"""
Creates points for .hpg
Do not Supports .pgl
"""


def parse_hpgl(gl_file):
    """Convert HP Graphics Language (HPGL) to list of paths"""

    border = 10

    pen_down = False
    cur_pen = 1
    cur_x = 0
    cur_y = 0
    cto_x = 0  # text offset
    cto_y = 0

    std_font = 48
    alt_font = 48
    cur_font = 48

    char_rel_width = 0.0075
    char_rel_height = 0.0075

    char_abs_width = 0
    char_abs_height = 0

    pen_width = 1
    stroke_weight = 0

    label_term = '\x03'
    label_term_print = False

    paths = []
    labels = []

    if type(gl_file) == str:
        glf = open(gl_file, 'r')
    else:
        glf = gl_file

    while True:
        c = glf.read(1)
        while c == ';' or c == ' ' or c == '\r' or c == '\n':
            c = glf.read(1)
        cmd = c + glf.read(1)
        cmd = cmd.upper()

        if len(cmd) < 2:
            break

        if cmd == 'PU':
            #  pen up
            pen_down = False
        elif cmd == 'PD':
            #  pen down
            pen_down = True
        elif cmd == 'SP':
            #  select pen
            c = glf.read(1)
            if c == ';':
                continue
            cur_pen = int(c)
        elif cmd == 'LT':
            pass
        elif cmd == 'SA':
            #  select alternate
            cur_font = alt_font
        elif cmd == 'SS':
            #  select standard
            cur_font = std_font
        elif cmd == 'SR':
            #  specify relative character sizes
            s = ''
            c = glf.read(1)
            while c != ',':
                s += c
                c = glf.read(1)
            char_rel_width = float(s)/100.0
            s = ''
            c = glf.read(1)
            while c != ';':
                s += c
                c = glf.read(1)
            char_rel_height = float(s)/100.0
        elif cmd == 'SI':
            #  specify absolute character sizes
            s = ''
            c = glf.read(1)
            while c != ',':
                s += c
                c = glf.read(1)
            char_abs_width = float(s)
            s = ''
            c = glf.read(1)
            while c != ';':
                s += c
                c = glf.read(1)
            char_abs_height = float(s)
        elif cmd == 'PA':
            #  plot absolute

            c = ''
            pts = [(cur_x, cur_y, cto_x, cto_y)]

            while c != ';':
                s = ''
                c = glf.read(1)
                if c == ';':
                    cur_x = 0
                    cur_y = 0
                    cto_x = 0
                    cto_y = 0
                    pts.append((0, 0, 0, 0))
                    break
                while c == '-' or c == "." or '0' <= c <= '9':
                    s += c
                    c = glf.read(1)

                cur_x = float(s)

                s = ''
                c = glf.read(1)
                while c == '-' or c == "." or '0' <= c <= '9':
                    s += c
                    c = glf.read(1)

                cur_y = float(s)

                cto_x = 0
                cto_y = 0

                pts.append((cur_x, cur_y, 0, 0))

            if pen_down:
                paths.append((cur_pen, pen_width, pts))
        elif cmd == 'LB':
            #  label

            c = glf.read(1)
            x = cur_x
            y = cur_y
            tx = cto_x
            ty = cto_y
            while label_term_print or c != label_term:
                if c == '\x08':
                    cto_x -= char_rel_width * 3/2
                elif c == '\x0A':
                    cto_x = tx
                    cto_y -= char_rel_height * 2
                elif c < ' ':
                    pass
                else:
                    labels.append(
                        (cur_x, cur_y, cto_x, cto_y, char_rel_width, char_rel_height, cur_pen, cur_font, c))
                    cto_x += char_rel_width * 3/2
                    if c == label_term:
                        break
                c = glf.read(1)
        elif cmd == 'DI':
            #  absolute direction
            s = ''
            c = glf.read(1)
            if c == ';':
                # run = 1
                # rise = 0
                continue
            while c != ',':
                s += c
                c = glf.read(1)
            # run = float(s)
            s = ''
            c = glf.read(1)
            while c != ';':
                s += c
                c = glf.read(1)
            # rise = float(s)
        elif cmd == 'DF':
            #  defaults
            pen_down = False
            cur_pen = 1
            cur_x = 0
            cur_y = 0
            cto_x = 0
            cto_y = 0

            std_font = 48
            alt_font = 48
            cur_font = 48

            char_rel_width = 0.0075
            char_rel_height = 0.0075

            label_term = '\x03'
            label_term_print = False
        elif cmd == 'IN':
            #  init
            pen_down = False
            cur_pen = 1
            cur_x = 0
            cur_y = 0
            cto_x = 0
            cto_y = 0

            std_font = 48
            alt_font = 48
            cur_font = 48

            char_rel_width = 0.0075
            char_rel_height = 0.0075

            label_term = '\x03'
            label_term_print = False
        elif cmd == 'OP':
            #  output P1 and P2 - ignored
            pass
        else:
            pass
            # print(f"Ignoring Unknown HPGL command f{cmd}")

    #  trackPoint=list()
    #  fname="MyCodes.txt"
    #  f=open(fname,"w+")
    # val = ""
    lines = list()
    shape = list()
    data = {"shape": shape}

    for x in paths:
        points = list()
        for point in x[2]:
            # val += f"points.push( new THREE.Vector3( {point[0]}, {point[1]}, 0 ) );\n"
            points.append({"pt1": point[0], "pt2": point[1]})
        # val += "\n"
        lines.append({"points": points, "pen_color": x[0]})
    shape.append({"lines": lines})
    # return val
    return json.dumps(data)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("please provide File")
    else:
        filename = sys.argv[1]
        f = open(f"{filename.split('.')[0]}.json", "w+")
        f.write(parse_hpgl(filename))
        print(f"Values dumped to {filename.split('.')[0]}.json")
        f.close()
