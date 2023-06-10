
var x1 >= 0;
var x2 >= 0;
var z;

set costs dimen 2;

maximize profit: z;
    
s.t. maxmin {(c1,c2) in costs}:
    z <= c1 * x1 + c2 * x2;

s.t. silicon: x1 <= 1000;
s.t. germanium: x2 <= 1500;
s.t. plastic: x1 + x2 <= 1750;
s.t. copper: 4 * x1 + 2 * x2 <= 4800;
