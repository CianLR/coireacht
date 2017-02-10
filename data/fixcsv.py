with open('garda_locations.csv', 'r') as f:
    lines = f.readlines()
    with open('fixed_garda_locations.csv', 'w') as g:
        for line in lines:
            parts = line.split()
            name = ' '.join(parts[:-2])
            x = 'x'
            y = 'x'
            if len(parts) >= 3:
                x = parts[-2]
                y = parts[-1]
            if x == 'x' or y == 'x' or name == 'x':
                continue
            g.write(name + ', '+  x + ', ' + y + '\n')
