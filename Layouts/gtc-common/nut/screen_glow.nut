// Glow shader code by zpaolo11x


// check if GLSL shaders are available on this system
if( my_config["enable_crt_screenglow"] != "No" && ShadersAvailable == 1 )
{
	// shadow parameters
	local shadow_radius = 1600
	local shadow_xoffset = 0
	local shadow_yoffset = 0
	local shadow_alpha = 255
	local shadow_downsample = 0

	if( my_config["enable_crt_screenglow"] == "Light" )
	{
		shadow_downsample=0.04
		shadow_xoffset = flx*0.156
		shadow_yoffset = fly*0.277
	}
	else if( my_config["enable_crt_screenglow"] == "Medium" )
	{
		shadow_downsample=0.027
		shadow_xoffset = flx*0.104
		shadow_yoffset = fly*0.231
	}
	else if( my_config["enable_crt_screenglow"] == "Strong" )
	{
		shadow_downsample=0.02
		shadow_xoffset = flx*0.052
		shadow_yoffset = fly*0.138
	}

	// creation of first surface with safeguards area
	local xsurf1 = fe.add_surface (shadow_downsample * (snap.width + 2*shadow_radius), shadow_downsample * (snap.height + 2*shadow_radius))

	// add a clone of the picture to topmost surface
	local pic1 = xsurf1.add_clone(snap)
	pic1.set_pos(shadow_radius*shadow_downsample,shadow_radius*shadow_downsample,snap.width*shadow_downsample,snap.height*shadow_downsample)

	// creation of second surface
	local xsurf2 = fe.add_surface (xsurf1.width, xsurf1.height)

	// nesting of surfaces
	xsurf1.visible = false
	xsurf1 = xsurf2.add_clone(xsurf1)
	xsurf1.visible = true

	// define and apply blur shaders
	local blursizex = 1.0/xsurf2.width
	local blursizey = 1.0/xsurf2.height
	local kernelsize = shadow_downsample * (shadow_radius * 2) + 1
	local kernelsigma = shadow_downsample * shadow_radius * 0.3

	local shaderH1 = fe.add_shader( Shader.Fragment, fe.script_dir + "gauss_kernsigma_o.glsl" )
	shaderH1.set_texture_param( "texture")
	shaderH1.set_param("kernelData", kernelsize, kernelsigma)
	shaderH1.set_param("offsetFactor", blursizex, 0.0)
	xsurf1.shader = shaderH1

	local shaderV1 = fe.add_shader( Shader.Fragment, fe.script_dir + "gauss_kernsigma_o.glsl" )
	shaderV1.set_texture_param( "texture")
	shaderV1.set_param("kernelData", kernelsize, kernelsigma)
	shaderV1.set_param("offsetFactor", 0.0, blursizey)
	xsurf2.shader = shaderV1

	// apply black color and alpha channel to shadow
	pic1.alpha=shadow_alpha
	pic1.width=21
	pic1.height=16

	// reposition and upsample shadow surface stack
	xsurf2.set_pos (snap.x-shadow_radius+shadow_xoffset,snap.y-shadow_radius+shadow_yoffset, snap.width + 2 * shadow_radius , snap.height + 2 * shadow_radius)
}
