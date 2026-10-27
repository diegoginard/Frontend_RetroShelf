//http://www.geeks3d.com/20110316/shader-library-simple-2d-effects-sphere-and-ripple-in-glsl/
uniform sampler2D texture;
uniform float ttime;

void main()
{   
    float time = ttime / 1000.0;
    vec2 tc = gl_TexCoord[0].xy;
    vec2 p = -1.0 + 2.0 * tc;
    float len = length(p);
    vec2 uv = tc + (p/len)*cos(len*12.0-time*4.0)*0.03;
    vec3 col = texture2D(texture,uv).xyz;
    gl_FragColor = vec4(col,1.0);
}