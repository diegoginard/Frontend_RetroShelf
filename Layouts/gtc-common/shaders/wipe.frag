uniform sampler2D texture;
uniform sampler2D src0;
uniform sampler2D src1;
uniform float fade;
uniform float range;
uniform float shift;

void main()
{
	vec4 wipe = texture2D( texture, gl_TexCoord[0].xy );
	vec4 s0 = texture2D( src0, gl_TexCoord[0].xy + vec2( -fade * shift + shift, 0.0 ));
	vec4 s1 = texture2D( src1, gl_TexCoord[0].xy + vec2( -fade * shift - shift, 0.0 ));

	float hr = range * 0.5;
	float f = fade * ( hr + 0.5 ) + 0.5;
	float ws = smoothstep( f - hr, f + hr, wipe.x );
	// gl_FragColor = gl_Color * vec4( ws, ws, ws, 1.0 );
	gl_FragColor = gl_Color * mix( s0, s1, ws );
	// if ( ws == 0.0 || ws == 1.0 ) gl_FragColor = vec4( 0.5, 0.0, 0.5, 1.0 );
	// float u = gl_TexCoord[0].x;
	// gl_FragColor = vec4(ws,ws,ws,1.0);
}
