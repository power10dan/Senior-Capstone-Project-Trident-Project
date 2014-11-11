function [northing,easting, k, gamma] = Geodetic2SPC(lat,long,zone)

%This function converts a list of latitudes and longitudes (in decimal degrees) to
%northings and eastings per the NAD83 Oregon State Plane Coordinate system.
%The user must specify which zone (3601 for North or 3602 for South)
%The function also returns the grid factor (k), and the convergency angle
%(gamma, in decimal degrees).

%load GRS80 constants 
a = 6378137; %meters
f = 1/298.257222101;
e = sqrt(2*f-f^2);

%load constants for NAD83, Oregon North Zones:

if zone == 3601; %Oregon North Zone (NAD83)
    lambdacm = 120.5;
    LatO = 43+40/60;
    LatS = 44+20/60;
    LatN = 46;
    Eo = 2500000; %meters
    Nb = 0;
   
elseif zone == 3602; %Oregon South Zone (NAD83)
    lambdacm = 120.5;
    LatO = 41+40/60;
    LatS = 42+20/60;
    LatN = 44;
    Eo = 1500000; %meters
    Nb = 0;
end


W = sqrt(1-e^2*(sind(lat)).^2);
M = cosd(lat)./W;
T = sqrt(((1-sind(lat))./(1+sind(lat))).*((1+e.*sind(lat))./(1-e.*sind(lat))).^e);

w1 = sqrt(1-e^2*(sind(LatS)).^2);
w2 = sqrt(1-e^2*(sind(LatN)).^2);

m1 = cosd(LatS)./w1;
m2 = cosd(LatN)./w2;
t0 = sqrt(((1-sind(LatO))./(1+sind(LatO))).*((1+e.*sind(LatO))./(1-e.*sind(LatO))).^e);
t1 = sqrt(((1-sind(LatS))./(1+sind(LatS))).*((1+e.*sind(LatS))./(1-e.*sind(LatS))).^e);
t2 = sqrt(((1-sind(LatN))./(1+sind(LatN))).*((1+e.*sind(LatN))./(1-e.*sind(LatN))).^e);

n = (log(m1)-log(m2))/(log(t1)-log(t2));
F = m1/(n*t1^n);
Rb = a*F*t0^n;

gamma = (lambdacm-long).*n; %convergency angle in decimal degrees

R = a.*F.*T.^n;

k = (R.*n)./(a.*M); %grid_factor

easting = R.*sind(gamma)+Eo;
northing = Rb-R.*cosd(gamma)+Nb;
end

