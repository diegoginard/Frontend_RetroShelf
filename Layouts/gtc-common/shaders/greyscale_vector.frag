uniform sampler2D texture;

void main()
{
    vec4 pixel = texture2D(texture, gl_TexCoord[0].xy);
    float g = clamp((pixel.r + pixel.g + pixel.b) / 1.2, 0.0, 1.0); 
    gl_FragColor = gl_Color * vec4(g, g, g, pixel.a);
}