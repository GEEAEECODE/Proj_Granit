import lib-normal.glsl
import lib-env.glsl

//: param auto channel_basecolor
uniform SamplerSparse lt_basecolor;
//: param auto channel_roughness
uniform SamplerSparse lt_roughness;
//: param auto channel_metallic
uniform SamplerSparse lt_metallic;
//: param auto world_eye_position
uniform vec3 lt_eye_position;
//: param auto world_camera_direction
uniform vec3 lt_camera_direction;
//: param auto camera_view_matrix
uniform mat4 lt_camera_view;
//: param auto is_perspective_projection
uniform bool lt_perspective;
//: param auto is_2d_view
uniform bool lt_2d_view;
//: param auto environment_max_lod
uniform float lt_env_max_lod;

//: param custom {"default":0.0,"min":0.0,"max":1.0,"label":"As Unlit","group":"Lighting","description":"lilToon As Unlit: blends light color toward white. Shadow and Rim Shade remain active.","visible":"false"}
uniform float lt_as_unlit;

//: param custom {"default":false,"label":"Use Shadow","group":"Shadow","visible":"false"}
uniform bool lt_use_shadow;
//: param custom {"default":1.0,"min":0.0,"max":1.0,"label":"Shadow Strength","group":"Shadow","visible":"false"}
uniform float lt_shadow_strength;
//: param custom {"default":false,"label":"Strength Mask","group":"Shadow","visible":"false","description":"User5 / SS / L8. Original lilToon common Strength Mask, shared by all shadow stages. OFF retains paint."}
uniform bool lt_shadow_use_strength_mask;
//: param auto channel_user5
uniform SamplerSparse lt_shadow_strength_mask;
//: param custom {"default":0.08,"min":0,"max":1,"label":"Border Range","group":"Shadow","visible":"false"}
uniform float lt_shadow_border_range;
//: param custom {"default":[1.0,0.010022820919105526,0.0],"widget":"color","label":"Border Color","group":"Shadow","visible":"false"}
uniform vec3 lt_shadow_border_color;

//: param custom {"default":true,"label":"Use Shadow 1","group":"Shadow/Shadow 1","description":"Enable this shadow color stage. The common Use Shadow switch still controls all stages. OFF preserves values and paint channels.","visible":"false"}
uniform bool lt_shadow1_enabled;
//: param custom {"default":1.0,"min":0.0,"max":1.0,"label":"Alpha","group":"Shadow/Shadow 1","description":"Independent stage opacity. 0 bypasses this color stage, 1 fully applies it. Painter extension; lilToon ignores Shadow 1 Color alpha.","visible":"false"}
uniform float lt_shadow1_alpha;
//: param custom {"default":[0.6382832153523972,0.5382355236010181,0.692071056865372],"widget":"color","label":"Color","group":"Shadow/Shadow 1","visible":"false"}
uniform vec3 lt_shadow1_color;
//: param custom {"default":0.5,"min":0.0,"max":1.0,"label":"Border","group":"Shadow/Shadow 1","visible":"false"}
uniform float lt_shadow1_border;
//: param custom {"default":0.1,"min":0.0,"max":1.0,"label":"Blur","group":"Shadow/Shadow 1","visible":"false"}
uniform float lt_shadow1_blur;
//: param custom {"default":1.0,"min":0.0,"max":1.0,"label":"Normal Strength","group":"Shadow/Shadow 1","visible":"false"}
uniform float lt_shadow1_normal;

//: param custom {"default":true,"label":"Use Shadow 2","group":"Shadow/Shadow 2","description":"Enable this shadow color stage. OFF preserves its Alpha, other values and paint channels.","visible":"false"}
uniform bool lt_shadow2_enabled;
//: param custom {"default":1.0,"min":0.0,"max":1.0,"label":"Alpha","group":"Shadow/Shadow 2","description":"Independent stage opacity, corresponding to lilToon Shadow 2 Color alpha.","visible":"false"}
uniform float lt_shadow2_alpha;
//: param custom {"default":[0.4200332886842154,0.393123090639499,0.5870162842030755],"widget":"color","label":"Color","group":"Shadow/Shadow 2","visible":"false"}
uniform vec3 lt_shadow2_color;
//: param custom {"default":0.15,"min":0.0,"max":1.0,"label":"Border","group":"Shadow/Shadow 2","visible":"false"}
uniform float lt_shadow2_border;
//: param custom {"default":0.1,"min":0.0,"max":1.0,"label":"Blur","group":"Shadow/Shadow 2","visible":"false"}
uniform float lt_shadow2_blur;
//: param custom {"default":1.0,"min":0.0,"max":1.0,"label":"Normal Strength","group":"Shadow/Shadow 2","visible":"false"}
uniform float lt_shadow2_normal;

//: param custom {"default":true,"label":"Use Shadow 3","group":"Shadow/Shadow 3","description":"Enable this shadow color stage. OFF preserves its Alpha, other values and paint channels.","visible":"false"}
uniform bool lt_shadow3_enabled;
//: param custom {"default":0.0,"min":0.0,"max":1.0,"label":"Alpha","group":"Shadow/Shadow 3","description":"Independent stage opacity, corresponding to lilToon Shadow 3 Color alpha. Original default is 0; raise it to see Shadow 3.","visible":"false"}
uniform float lt_shadow3_alpha;
//: param custom {"default":[0.0,0.0,0.0],"widget":"color","label":"Color","group":"Shadow/Shadow 3","visible":"false"}
uniform vec3 lt_shadow3_color;
//: param custom {"default":0.25,"min":0.0,"max":1.0,"label":"Border","group":"Shadow/Shadow 3","visible":"false"}
uniform float lt_shadow3_border;
//: param custom {"default":0.1,"min":0.0,"max":1.0,"label":"Blur","group":"Shadow/Shadow 3","visible":"false"}
uniform float lt_shadow3_blur;
//: param custom {"default":1.0,"min":0.0,"max":1.0,"label":"Normal Strength","group":"Shadow/Shadow 3","visible":"false"}
uniform float lt_shadow3_normal;

//: param custom {"default":false,"label":"Color Channel","group":"Shadow/Shadow 1","visible":"false","description":"User2 / S1C / sRGB8. Enable in the plugin to create or configure the paint channel. OFF preserves paint data."}
uniform bool lt_shadow1_use_channel;
//: param auto channel_user2
uniform SamplerSparse lt_shadow1_channel;
//: param custom {"default":0.0,"min":-10.0,"max":10.0,"label":"Height Strength","group":"Shadow/Shadow 1","visible":"false"}
uniform float lt_shadow1_height;
//: param custom {"default":false,"label":"Color Channel","group":"Shadow/Shadow 2","visible":"false","description":"User3 / S2C / sRGB8. Enable in the plugin to create or configure the paint channel. OFF preserves paint data."}
uniform bool lt_shadow2_use_channel;
//: param auto channel_user3
uniform SamplerSparse lt_shadow2_channel;
//: param custom {"default":0.0,"min":-10.0,"max":10.0,"label":"Height Strength","group":"Shadow/Shadow 3","visible":"false"}
uniform float lt_shadow3_height;
//: param custom {"default":false,"label":"Color Channel","group":"Shadow/Shadow 3","visible":"false","description":"User4 / S3C / sRGB8. Enable in the plugin to create or configure the paint channel. OFF preserves paint data."}
uniform bool lt_shadow3_use_channel;
//: param auto channel_user4
uniform SamplerSparse lt_shadow3_channel;
//: param custom {"default":0.0,"min":-10.0,"max":10.0,"label":"Height Strength","group":"Shadow/Shadow 2","visible":"false"}
uniform float lt_shadow2_height;

//: param custom {"default":false,"label":"Border Mask","group":"Shadow/Shadow 1","visible":"false","description":"User6 / S1BD / L8. lilToon Border Mask: multiplies the lighting input before the Border threshold. Black deepens shadow; white preserves. Missing/unpainted areas are white. OFF preserves paint."}
uniform bool lt_shadow1_use_border_mask;
//: param auto channel_user6
uniform SamplerSparse lt_shadow1_border_mask;
//: param custom {"default":false,"label":"Blur Mask","group":"Shadow/Shadow 1","visible":"false","description":"User9 / S1BR / L8. Multiplies this stage Blur. Black sharpens the boundary; white preserves. Missing/unpainted areas are white. OFF preserves paint."}
uniform bool lt_shadow1_use_blur_mask;
//: param auto channel_user9
uniform SamplerSparse lt_shadow1_blur_mask;
//: param custom {"default":false,"label":"Border Mask","group":"Shadow/Shadow 2","visible":"false","description":"User7 / S2BD / L8. lilToon Border Mask: multiplies the lighting input before the Border threshold. Black deepens shadow; white preserves. Missing/unpainted areas are white. OFF preserves paint."}
uniform bool lt_shadow2_use_border_mask;
//: param auto channel_user7
uniform SamplerSparse lt_shadow2_border_mask;
//: param custom {"default":false,"label":"Blur Mask","group":"Shadow/Shadow 2","visible":"false","description":"User10 / S2BR / L8. Multiplies this stage Blur. Black sharpens the boundary; white preserves. Missing/unpainted areas are white. OFF preserves paint."}
uniform bool lt_shadow2_use_blur_mask;
//: param auto channel_user10
uniform SamplerSparse lt_shadow2_blur_mask;
//: param custom {"default":false,"label":"Border Mask","group":"Shadow/Shadow 3","visible":"false","description":"User8 / S3BD / L8. lilToon Border Mask: multiplies the lighting input before the Border threshold. Black deepens shadow; white preserves. Missing/unpainted areas are white. OFF preserves paint."}
uniform bool lt_shadow3_use_border_mask;
//: param auto channel_user8
uniform SamplerSparse lt_shadow3_border_mask;
//: param custom {"default":false,"label":"Blur Mask","group":"Shadow/Shadow 3","visible":"false","description":"User11 / S3BR / L8. Multiplies this stage Blur. Black sharpens the boundary; white preserves. Missing/unpainted areas are white. OFF preserves paint."}
uniform bool lt_shadow3_use_blur_mask;
//: param auto channel_user11
uniform SamplerSparse lt_shadow3_blur_mask;

//: param custom {"default":false,"label":"Use Rim Shade","group":"Rim Shade","visible":"false"}
uniform bool lt_use_rim;
//: param custom {"default":[0.21404114048223255,0.21404114048223255,0.21404114048223255],"widget":"color","label":"Color","group":"Rim Shade","visible":"false"}
uniform vec3 lt_rim_color;
//: param custom {"default":1.0,"min":0.0,"max":1.0,"label":"Strength","group":"Rim Shade","description":"Maps to lilToon Rim Shade Color alpha.","visible":"false"}
uniform float lt_rim_strength;
//: param custom {"default":0.5,"min":0.0,"max":1.0,"label":"Border","group":"Rim Shade","visible":"false"}
uniform float lt_rim_border;
//: param custom {"default":1.0,"min":0.0,"max":1.0,"label":"Blur","group":"Rim Shade","visible":"false"}
uniform float lt_rim_blur;
//: param custom {"default":1.0,"min":0.0,"max":1.0,"label":"Normal Strength","group":"Rim Shade","visible":"false"}
uniform float lt_rim_normal;
//: param custom {"default":1.0,"min":0.01,"max":50.0,"label":"Fresnel Power","group":"Rim Shade","visible":"false"}
uniform float lt_rim_power;

//: param custom {"default":false,"label":"Use Reflection","group":"Reflection","description":"Master switch for metallic diffuse reduction, direct specular and environment reflection, as in lilToon.","visible":"false"}
uniform bool lt_use_reflection;
//: param custom {"default":0.04,"min":0.0,"max":1.0,"label":"Reflectance","group":"Reflection","description":"Matches lilToon's [Gamma] Inspector value, converted to linear before computing F0.","visible":"false"}
uniform float lt_reflectance;
//: param custom {"default":1.0,"min":0.0,"max":1.0,"label":"Specular Strength","group":"Reflection","description":"Scales direct specular only. 0 replaces Apply Specular OFF; 1 matches ON.","visible":"false"}
uniform float lt_specular_strength;
//: param custom {"default":1,"widget":"combobox","values":{"Realistic":0,"Toon":1},"label":"Specular Mode","group":"Reflection","visible":"false"}
uniform int lt_specular_mode;
//: param custom {"default":0.5,"min":0.0,"max":1.0,"label":"Specular Border","group":"Reflection","visible":"false"}
uniform float lt_specular_border;
//: param custom {"default":0.0,"min":0.0,"max":1.0,"label":"Specular Blur","group":"Reflection","visible":"false"}
uniform float lt_specular_blur;
//: param custom {"default":false,"label":"Apply Environment Reflection","group":"Reflection","description":"lilToon Apply Reflection (default OFF). Enable to preview environment reflection and metal color.","visible":"false"}
uniform bool lt_apply_reflection;
//: param custom {"default":[1,1,1,1],"widget":"color","label":"Reflection Color","group":"Reflection","visible":"false"}
uniform vec4 lt_reflection_color;

//: param auto channel_user12
uniform SamplerSparse lt_matcap1_mask;
//: param auto channel_user13
uniform SamplerSparse lt_matcap2_mask;
//: param custom {"default":false,"label":"Use MatCap","group":"MatCap 1","visible":"false","description":"Enable MatCap and prepare User12 / MB1 / L8 Blend Mask. White allows, black hides; unpainted areas allow. OFF preserves paint."}
uniform bool lt_matcap1_enabled;
//: param custom {"default":"","label":"Image","group":"MatCap 1","visible":"false","default_color":[1,1,1,1],"usage":"texture"}
uniform sampler2D lt_matcap1_texture;
//: param custom {"default":[1,1,1,1],"label":"Color","group":"MatCap 1","visible":"false","widget":"color"}
uniform vec4 lt_matcap1_color;
//: param custom {"default":1,"label":"Blend","group":"MatCap 1","visible":"false","min":0,"max":1}
uniform float lt_matcap1_blend;
//: param custom {"default":1,"label":"Blend Mode","group":"MatCap 1","visible":"false","widget":"combobox","values":{"Normal":0,"Add":1,"Screen":2,"Multiply":3}}
uniform int lt_matcap1_mode;
//: param custom {"default":1,"label":"Normal Strength","group":"MatCap 1","visible":"false","min":0,"max":1}
uniform float lt_matcap1_normal;
//: param custom {"default":0,"label":"Main Color Strength","group":"MatCap 1","visible":"false","min":0,"max":1}
uniform float lt_matcap1_main;
//: param custom {"default":1,"label":"Lighting","group":"MatCap 1","visible":"false","min":0,"max":1}
uniform float lt_matcap1_lighting;
//: param custom {"default":0,"label":"Shadow Mask","group":"MatCap 1","visible":"false","description":"Suppress MatCap on the Shadow 1 side. Uses lilToon shadowmix before Shadow Strength.","min":0,"max":1}
uniform float lt_matcap1_shadow;
//: param custom {"default":0,"label":"Blur","group":"MatCap 1","visible":"false","description":"MatCap mip level, matching lilToon LOD blur.","min":0,"max":10}
uniform float lt_matcap1_blur;
//: param custom {"default":true,"label":"Cancel Camera Roll","group":"MatCap 1","visible":"false"}
uniform bool lt_matcap1_zrot;
//: param custom {"default":true,"label":"Perspective Correction","group":"MatCap 1","visible":"false"}
uniform bool lt_matcap1_perspective;
//: param custom {"default":true,"label":"Image sRGB","group":"MatCap 1","visible":"false","description":"Decode the image RGB as sRGB. Disable for linear/HDR images; alpha is unchanged. This does not change viewport color management."}
uniform bool lt_matcap1_srgb;
//: param custom {"default":false,"label":"Use MatCap","group":"MatCap 2","visible":"false","description":"Enable MatCap and prepare User13 / MB2 / L8 Blend Mask. White allows, black hides; unpainted areas allow. OFF preserves paint."}
uniform bool lt_matcap2_enabled;
//: param custom {"default":"","label":"Image","group":"MatCap 2","visible":"false","default_color":[1,1,1,1],"usage":"texture"}
uniform sampler2D lt_matcap2_texture;
//: param custom {"default":[1,1,1,1],"label":"Color","group":"MatCap 2","visible":"false","widget":"color"}
uniform vec4 lt_matcap2_color;
//: param custom {"default":1,"label":"Blend","group":"MatCap 2","visible":"false","min":0,"max":1}
uniform float lt_matcap2_blend;
//: param custom {"default":1,"label":"Blend Mode","group":"MatCap 2","visible":"false","widget":"combobox","values":{"Normal":0,"Add":1,"Screen":2,"Multiply":3}}
uniform int lt_matcap2_mode;
//: param custom {"default":1,"label":"Normal Strength","group":"MatCap 2","visible":"false","min":0,"max":1}
uniform float lt_matcap2_normal;
//: param custom {"default":0,"label":"Main Color Strength","group":"MatCap 2","visible":"false","min":0,"max":1}
uniform float lt_matcap2_main;
//: param custom {"default":1,"label":"Lighting","group":"MatCap 2","visible":"false","min":0,"max":1}
uniform float lt_matcap2_lighting;
//: param custom {"default":0,"label":"Shadow Mask","group":"MatCap 2","visible":"false","description":"Suppress MatCap on the Shadow 1 side. Uses lilToon shadowmix before Shadow Strength.","min":0,"max":1}
uniform float lt_matcap2_shadow;
//: param custom {"default":0,"label":"Blur","group":"MatCap 2","visible":"false","description":"MatCap mip level, matching lilToon LOD blur.","min":0,"max":10}
uniform float lt_matcap2_blur;
//: param custom {"default":true,"label":"Cancel Camera Roll","group":"MatCap 2","visible":"false"}
uniform bool lt_matcap2_zrot;
//: param custom {"default":true,"label":"Perspective Correction","group":"MatCap 2","visible":"false"}
uniform bool lt_matcap2_perspective;
//: param custom {"default":true,"label":"Image sRGB","group":"MatCap 2","visible":"false","description":"Decode the image RGB as sRGB. Disable for linear/HDR images; alpha is unchanged. This does not change viewport color management."}
uniform bool lt_matcap2_srgb;

struct LTMaterial {
    vec3 albedo;
    vec3 geometricNormal;
    vec3 normal;
    vec3 shadowNormal1;
    vec3 shadowNormal2;
    vec3 shadowNormal3;
    SparseCoord sparseCoord;
    vec3 view;
    float perceptualRoughness;
    float metallic;
};
struct LTLight {
    vec3 direction;
    vec3 color;
};
struct LTResult {
    vec3 diffuse;
    vec3 specular;
};

vec3 ltSafeNormal(vec3 v, vec3 fallback) {
    return dot(v,v) > 1e-12 ? v * inversesqrt(dot(v,v)) : fallback;
}
float ltSaturate(float x) { return clamp(x,0.0,1.0); }
float ltSRGBToLinear(float x) {
    return x <= 0.04045 ? x / 12.92 : pow((x+0.055)/1.055,2.4);
}

float ltToon(float value, float border, float blur, float range) {
    float lower = ltSaturate(border - blur * 0.5 - range);
    float upper = ltSaturate(border + blur * 0.5);
    float width = ltSaturate(upper - lower + fwidth(value));
    return width > 0.0 ? ltSaturate((value-lower)/width) : step(lower,value);
}
float ltHalfLambert(LTMaterial s, LTLight light, float normalStrength, vec3 stageNormal) {

    vec3 n = mix(s.geometricNormal,stageNormal,normalStrength);
    return ltSaturate(dot(light.direction,n)*0.5+0.5);
}

float ltPaintMask(SamplerSparse mask, SparseCoord coord) {
    if (!mask.is_set) return 1.0;

    vec4 value = textureSparse(mask,coord);
    return ltSaturate(value.r+1.0-value.g);
}
float ltShadowMask(bool enabled, SamplerSparse mask, SparseCoord coord) {
    return enabled ? ltPaintMask(mask,coord) : 1.0;
}

vec3 ltShadow(LTMaterial s, LTLight light) {
    vec3 direct = s.albedo * light.color;
    if (!lt_use_shadow || !(lt_shadow1_enabled || lt_shadow2_enabled || lt_shadow3_enabled)) return direct;
    float a1 = lt_shadow1_enabled ? lt_shadow1_alpha : 0.0;
    float a2 = lt_shadow2_enabled ? lt_shadow2_alpha : 0.0;
    float a3 = lt_shadow3_enabled ? lt_shadow3_alpha : 0.0;
    float h1 = ltHalfLambert(s,light,lt_shadow1_normal,s.shadowNormal1);
    float h2 = ltHalfLambert(s,light,lt_shadow2_normal,s.shadowNormal2);
    float h3 = ltHalfLambert(s,light,lt_shadow3_normal,s.shadowNormal3);

    h1 *= ltShadowMask(lt_shadow1_use_border_mask,lt_shadow1_border_mask,s.sparseCoord);
    h2 *= ltShadowMask(lt_shadow2_use_border_mask,lt_shadow2_border_mask,s.sparseCoord);
    h3 *= ltShadowMask(lt_shadow3_use_border_mask,lt_shadow3_border_mask,s.sparseCoord);
    float blur1 = lt_shadow1_blur*ltShadowMask(lt_shadow1_use_blur_mask,lt_shadow1_blur_mask,s.sparseCoord);
    float blur2 = lt_shadow2_blur*ltShadowMask(lt_shadow2_use_blur_mask,lt_shadow2_blur_mask,s.sparseCoord);
    float blur3 = lt_shadow3_blur*ltShadowMask(lt_shadow3_use_blur_mask,lt_shadow3_blur_mask,s.sparseCoord);
    float t1 = ltToon(h1,lt_shadow1_border,blur1,0.0);
    float t2 = ltToon(h2,lt_shadow2_border,blur2,0.0);
    float t3 = ltToon(h3,lt_shadow3_border,blur3,0.0);
    float border = ltToon(h1,lt_shadow1_border,blur1,lt_shadow_border_range);
    vec4 tex1 = a1 > 0.0 && lt_shadow1_use_channel && lt_shadow1_channel.is_set ? textureSparse(lt_shadow1_channel,s.sparseCoord) : vec4(0);
    vec4 tex2 = a2 > 0.0 && lt_shadow2_use_channel && lt_shadow2_channel.is_set ? textureSparse(lt_shadow2_channel,s.sparseCoord) : vec4(0);
    vec4 tex3 = a3 > 0.0 && lt_shadow3_use_channel && lt_shadow3_channel.is_set ? textureSparse(lt_shadow3_channel,s.sparseCoord) : vec4(0);

    vec3 shade = mix(s.albedo,(tex1.rgb+s.albedo*(1.0-tex1.a))*lt_shadow1_color,a1);
    shade = mix(shade,(tex2.rgb+s.albedo*(1.0-tex2.a))*lt_shadow2_color,a2*(1.0-t2));
    shade = mix(shade,(tex3.rgb+s.albedo*(1.0-tex3.a))*lt_shadow3_color,a3*(1.0-t3));
    shade = min(shade*light.color,direct);

    shade = mix(shade,direct,border*lt_shadow_border_color);
    return mix(shade,direct,mix(1.0,t1,lt_shadow_strength*ltShadowMask(lt_shadow_use_strength_mask,lt_shadow_strength_mask,s.sparseCoord)));
}

vec3 ltRimShade(LTMaterial s, vec3 diffuse) {
    if (!lt_use_rim) return diffuse;
    vec3 n = mix(s.geometricNormal,s.normal,lt_rim_normal);
    float edge = pow(ltSaturate(1.0-abs(dot(n,s.view))),lt_rim_power);
    float amount = ltToon(edge,lt_rim_border,lt_rim_blur,0.0)*lt_rim_strength;
    return mix(diffuse,diffuse*lt_rim_color,amount);
}

vec3 ltFresnel(vec3 f0, vec3 f90, float cosine) {
    float x = 1.0-cosine;
    return mix(f0,f90,x*x*x*x*x);
}

vec3 ltDirectSpecular(LTMaterial s, LTLight light, vec3 f0) {
    vec3 h = ltSafeNormal(s.view+light.direction,s.normal);
    float nh = ltSaturate(dot(s.normal,h));
    float roughness = s.perceptualRoughness*s.perceptualRoughness;
    if (lt_specular_mode == 1) {
        float lobe = pow(nh,1.0/max(roughness,1e-6));
        return vec3(ltToon(lobe,lt_specular_border,lt_specular_blur,0.0));
    }
    float nv = ltSaturate(dot(s.normal,s.view));
    float nl = ltSaturate(dot(s.normal,light.direction));
    float lh = ltSaturate(dot(light.direction,h));
    float r = max(roughness,0.002);
    float lambdaV = nl*(nv*(1.0-r)+r);
    float lambdaL = nv*(nl*(1.0-r)+r);
    float r2 = r*r;
    float d = (nh*r2-nh)*nh+1.0;
    float ggx = r2/(d*d+1e-7);
    float visibility = 0.5/(lambdaV+lambdaL+1e-5);
    return visibility*ggx*nl*ltFresnel(f0,vec3(1.0),lh);
}

vec2 ltMatCapUV(vec3 normal, vec3 view, bool zRotCancel, bool perspective) {
    vec3 cameraBack = ltSafeNormal(-lt_camera_direction,vec3(0,0,1));
    vec3 direction = ltSafeNormal(lt_perspective && perspective ? view : cameraBack,cameraBack);
    vec3 cameraUp = vec3(lt_camera_view[0][1],lt_camera_view[1][1],lt_camera_view[2][1]);
    vec3 up = zRotCancel ? vec3(0,1,0) : cameraUp;
    vec3 bitangent = up-direction*dot(direction,up);

    if (dot(bitangent,bitangent)<1e-10) {
        up = abs(direction.z)<0.99 ? vec3(0,0,1) : vec3(1,0,0);
        bitangent = up-direction*dot(direction,up);
    }
    bitangent = normalize(bitangent);
    vec3 tangent = cross(direction,bitangent);
    return vec2(dot(tangent,normal),dot(bitangent,normal))*0.5+0.5;
}

vec3 ltBlendColor(vec3 destination, vec3 source, float amount, int mode) {
    vec3 blended = source;
    if (mode==1) blended = destination+source;
    if (mode==2) blended = max(destination+source-destination*source,destination);
    if (mode==3) blended = destination*source;
    return mix(destination,blended,amount);
}

float ltShadowMix(LTMaterial s, LTLight light) {
    if (!lt_use_shadow || !lt_shadow1_enabled) return 1.0;

    float h = ltHalfLambert(s,light,lt_shadow1_normal,s.shadowNormal1);
    h *= ltShadowMask(lt_shadow1_use_border_mask,lt_shadow1_border_mask,s.sparseCoord);
    float blur = lt_shadow1_blur*ltShadowMask(lt_shadow1_use_blur_mask,lt_shadow1_blur_mask,s.sparseCoord);
    float alpha = lt_shadow1_alpha;
    float boundary = ltToon(h,lt_shadow1_border,blur,0.0);
    return mix(1.0,boundary,alpha);
}

float ltMatCapMask(SamplerSparse mask, SparseCoord coord) {
    return ltPaintMask(mask,coord);
}

vec3 ltMatCapLayer(LTMaterial s, LTLight light, vec3 destination,
                  sampler2D image, vec4 tint, float blend, int mode,
                  float normalStrength, float mainStrength, float lighting,
                  float shadowMask, float blur, bool zRot, bool perspective,
                  bool srgb, bool normalizeNormal, float paintMask) {
    vec3 normal = mix(s.geometricNormal,s.normal,normalStrength);

    if (normalizeNormal) normal = ltSafeNormal(normal,s.geometricNormal);
    vec2 uv = ltMatCapUV(normal,s.view,zRot,perspective);
    vec4 sampled = textureLod(image,uv,blur);
    if (srgb) sampled.rgb = vec3(ltSRGBToLinear(sampled.r),ltSRGBToLinear(sampled.g),ltSRGBToLinear(sampled.b));
    vec4 color = sampled*tint;
    color.rgb *= mix(vec3(1),light.color,lighting);
    color.a *= mix(1.0,ltShadowMix(s,light),shadowMask);
    color.rgb *= mix(vec3(1),s.albedo,mainStrength);
    return ltBlendColor(destination,color.rgb,blend*color.a*paintMask,mode);
}

vec3 ltMatCaps(LTMaterial s, LTLight light, vec3 color) {
    if (lt_matcap1_enabled)
        color = ltMatCapLayer(s,light,color,lt_matcap1_texture,lt_matcap1_color,
            lt_matcap1_blend,lt_matcap1_mode,lt_matcap1_normal,lt_matcap1_main,
            lt_matcap1_lighting,lt_matcap1_shadow,lt_matcap1_blur,lt_matcap1_zrot,
            lt_matcap1_perspective,lt_matcap1_srgb,true,ltMatCapMask(lt_matcap1_mask,s.sparseCoord));
    if (lt_matcap2_enabled)
        color = ltMatCapLayer(s,light,color,lt_matcap2_texture,lt_matcap2_color,
            lt_matcap2_blend,lt_matcap2_mode,lt_matcap2_normal,lt_matcap2_main,
            lt_matcap2_lighting,lt_matcap2_shadow,lt_matcap2_blur,lt_matcap2_zrot,
            lt_matcap2_perspective,lt_matcap2_srgb,false,ltMatCapMask(lt_matcap2_mask,s.sparseCoord));
    return color;
}

vec3 ltStageNormal(V2F inputs, vec3 normal, float strength) {
    if (strength == 0.0) return normal;
    vec3 ts = getTSNormal(inputs.sparse_coord,normalFromHeight(inputs.sparse_coord,strength));
    return ltSafeNormal(ts.x*inputs.tangent+ts.y*inputs.bitangent+ts.z*inputs.normal,normal);
}
LTMaterial ltReadMaterial(V2F inputs) {
    LTMaterial s;
    vec4 color = textureSparse(lt_basecolor,inputs.sparse_coord);
    vec4 rough = textureSparse(lt_roughness,inputs.sparse_coord);
    vec4 metal = textureSparse(lt_metallic,inputs.sparse_coord);
    s.albedo = color.rgb + vec3(0.5)*(1.0-color.a);
    s.perceptualRoughness = ltSaturate(rough.r+0.3*(1.0-rough.g));
    s.metallic = ltSaturate(metal.r);
    s.geometricNormal = ltSafeNormal(inputs.normal,vec3(0,0,1));

    vec3 nts = getTSNormal(inputs.sparse_coord,vec3(0,0,1));
    s.normal = ltSafeNormal(nts.x*inputs.tangent+nts.y*inputs.bitangent+
                            nts.z*inputs.normal,s.geometricNormal);
    s.shadowNormal1 = ltStageNormal(inputs,s.normal,lt_shadow1_height);
    s.shadowNormal2 = ltStageNormal(inputs,s.normal,lt_shadow2_height);
    s.shadowNormal3 = ltStageNormal(inputs,s.normal,lt_shadow3_height);
    s.sparseCoord = inputs.sparse_coord;
    s.view = lt_2d_view ? s.geometricNormal : ltSafeNormal(
        lt_perspective ? lt_eye_position-inputs.position : -lt_camera_direction,
        s.geometricNormal);
    return s;
}

vec3 ltSHLinearDirection(mat4 m) {
    return vec3(m[0][3]+m[3][0],m[1][3]+m[3][1],m[2][3]+m[3][2]);
}
LTLight ltReadLighting() {
    LTLight light;

    vec3 sh = (ltSHLinearDirection(irrad_mat_red)+ltSHLinearDirection(irrad_mat_green)+
               ltSHLinearDirection(irrad_mat_blue))/3.0;
    vec3 worldSH = transpose(environment_matrix)*sh.xzy;
    vec3 directionSH = dot(worldSH,worldSH)<1e-6 ? vec3(0) : normalize(worldSH);
    light.direction = ltSafeNormal(worldSH+vec3(0.001,0.002,0.001),vec3(0,1,0));

    light.color = mix(clamp(envIrradiance(directionSH*0.666666),vec3(0.05),vec3(1.0)),
                      vec3(1.0),lt_as_unlit);
    return light;
}

float ltRadicalInverse(int index) {
    float value = 0.0;
    float factor = 0.5;
    for (int bit=0;bit<5;++bit) {
        value += float(index & 1)*factor;
        index >>= 1;
        factor *= 0.5;
    }
    return value;
}
vec3 ltEnvironmentReflection(LTMaterial s) {
    vec3 r = ltSafeNormal(worldToEnvSpace(reflect(-s.view,s.normal)),vec3(0,1,0));
    if (s.perceptualRoughness < 0.001) return envSample(r,0.0);
    vec3 t = normalize(cross(abs(r.y)<0.99 ? vec3(0,1,0) : vec3(1,0,0),r));
    vec3 b = cross(r,t);
    float a = s.perceptualRoughness*s.perceptualRoughness;
    float a2 = a*a;
    vec3 sum = vec3(0);
    float weights = 0.0;
    vec2 dimensions = vec2(textureSize(environment_texture,0));
    for (int i=0;i<32;++i) {
        float u = (float(i)+0.5)/32.0;
        float phi = 6.28318530718*ltRadicalInverse(i);
        float cosTheta = sqrt((1.0-u)/(1.0+(a2-1.0)*u));
        float sinTheta = sqrt(max(0.0,1.0-cosTheta*cosTheta));
        vec3 h = t*(sinTheta*cos(phi))+b*(sinTheta*sin(phi))+r*cosTheta;
        vec3 l = ltSafeNormal(2.0*dot(r,h)*h-r,r);
        float nl = max(0.0,dot(r,l));
        float d = cosTheta*cosTheta*(a2-1.0)+1.0;
        float pdf = a2/max(12.5663706144*d*d,1e-12);
        float sampleArea = 1.0/max(32.0*pdf,1e-12);
        float texelArea = 19.7392088022*sqrt(max(1e-8,1.0-l.y*l.y))/
                          max(1.0,dimensions.x*dimensions.y);
        float lod = clamp(0.5*log2(sampleArea/texelArea),0.0,lt_env_max_lod);
        sum += envSample(l,lod)*nl;
        weights += nl;
    }
    return sum/max(weights,1e-6);
}

vec3 ltEvaluateDiffuse(LTMaterial s, LTLight light) {
    vec3 diffuse = ltRimShade(s,ltShadow(s,light));
    if (lt_use_reflection) diffuse *= 1.0-s.metallic;
    return diffuse;
}

vec3 ltEvaluateReflection(LTMaterial s, LTLight light) {
    vec3 specular = vec3(0);
    if (lt_use_reflection) {
        vec3 f0 = mix(vec3(ltSRGBToLinear(lt_reflectance)),s.albedo,s.metallic);
        if (lt_specular_strength > 0.0)
            specular = ltDirectSpecular(s,light,f0)*light.color*lt_specular_strength;
        if (lt_apply_reflection) {
            float smoothness = 1.0-s.perceptualRoughness;
            float roughness = s.perceptualRoughness*s.perceptualRoughness;
            float grazing = ltSaturate(smoothness+1.0-0.96*(1.0-s.metallic));
            float reduction = 1.0/(roughness*roughness+1.0);
            specular += reduction*ltEnvironmentReflection(s)*
                ltFresnel(f0,vec3(grazing),ltSaturate(dot(s.normal,s.view)));
        }
    }
    return specular*lt_reflection_color.rgb*lt_reflection_color.a;
}

LTResult ltComposeMatCaps(LTMaterial s, LTLight light, LTResult result) {
    if (lt_matcap1_enabled || lt_matcap2_enabled) {

        result.diffuse = ltMatCaps(s,light,result.diffuse+result.specular);
        result.specular = vec3(0);
    }
    return result;
}

LTResult ltEvaluate(LTMaterial s, LTLight light) {
    LTResult result;
    result.diffuse = ltEvaluateDiffuse(s,light);
    result.specular = ltEvaluateReflection(s,light);
    return ltComposeMatCaps(s,light,result);
}

void ltWriteOpaqueOutput(LTResult result) {

    albedoOutput(vec3(1));
    diffuseShadingOutput(result.diffuse);
    specularShadingOutput(result.specular);
    emissiveColorOutput(vec3(0));
    alphaOutput(1.0);
}

void shade(V2F inputs) {
    LTMaterial surface = ltReadMaterial(inputs);
    LTLight light = ltReadLighting();
    ltWriteOpaqueOutput(ltEvaluate(surface,light));
}
