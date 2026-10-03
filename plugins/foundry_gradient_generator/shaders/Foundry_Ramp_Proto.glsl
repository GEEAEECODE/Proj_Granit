import lib-sampler.glsl
import lib-normal.glsl
import lib-env.glsl
import lib-emissive.glsl

//: state blend over
//: state cull_face off

//: param auto channel_basecolor
uniform SamplerSparse basecolor_texture;

//: param auto channel_roughness
uniform SamplerSparse roughness_texture;

//: param auto channel_metallic
uniform SamplerSparse metallic_texture;

//: param auto channel_opacity
uniform SamplerSparse opacity_texture;

//: param custom { "default": 0, "label": "Diffuse", "widget": "combobox", "values": { "All NPR": 0, "All PBR": 1, "Lerp": 2 }, "group": "NPR bar", "description": "Diffuse only. Lerp uses the exact Ramp input after Offset/Contrast: 0=NPR, 1=PBR. Emissive and Opacity are independent. Specular is not implemented yet." }
uniform int diffuse_mode;

//: param custom { "default": "Ramp_Test", "default_color": [1.0, 1.0, 1.0, 1.0], "label": "Ramp Texture", "usage": "texture", "group": "Ramp", "description": "Import a ramp as Texture, then select it here. X: shadow to light; Y: center. An unassigned texture is white." }
uniform sampler2D ramp_texture;

//: param custom { "default": 1, "label": "Ramp Filtering", "widget": "combobox", "values": { "Smooth (linear)": 0, "Hard (nearest)": 1 }, "group": "Ramp", "description": "Nearest preserves hard steps. Linear interpolates adjacent texels. Both use mip level zero and clamp at the ends." }
uniform int ramp_filtering;

//: param custom { "default": 0.0, "label": "Ramp Offset", "min": -1.0, "max": 1.0, "group": "Ramp", "description": "Added after contrast. Positive values sample toward the light end. Also changes the NPR/PBR weight in Lerp mode." }
uniform float ramp_offset;

//: param custom { "default": 1.0, "label": "Ramp Contrast", "min": 0.0, "max": 4.0, "group": "Ramp", "description": "Contrast around 0.5 before sampling. One is neutral; zero samples the center plus offset. The adjusted input is also the PBR weight in Lerp mode." }
uniform float ramp_contrast;

//: param custom { "default": 1.0, "label": "Ramp Strength", "min": 0.0, "max": 1.0, "group": "Ramp", "description": "One uses the ramp as authored. Zero removes ramp modulation; Metallic, AO and NPR intensity still apply. Does not change the Lerp weight." }
uniform float shadow_strength;

//: param custom { "default": [0.5, 0.5, 1.0], "label": "Light Direction", "min": -1.0, "max": 1.0, "group": "NPR Lighting", "description": "Environment-local direction FROM surface TOWARD light. Follows Painter environment rotation; zero falls back to local +Z. Drives NPR lighting and the Lerp coordinate. PBR diffuse uses the HDRI instead." }
uniform vec3 light_direction;

//: param custom { "default": 1.0, "label": "Light Intensity", "min": 0.0, "max": 4.0, "group": "NPR Lighting", "description": "NPR diffuse intensity only. Does not move the Ramp coordinate or Lerp weight. PBR diffuse intensity comes from Painter environment exposure." }
uniform float light_intensity;

//: param custom { "default": 0, "label": "Preview", "widget": "combobox", "values": { "Final": 0, "Lighting Value": 1, "Ramp Coordinate": 2, "Ramp Color": 3, "Base Color": 4, "World Normal": 5, "Roughness": 6, "Metallic": 7, "AO": 8, "Emissive": 9, "Opacity": 10, "NPR Diffuse": 11, "PBR Diffuse": 12, "PBR Weight": 13, "Mixed Diffuse": 14 }, "group": "Diagnostics", "description": "Diagnostics are opaque and suppress separate Emissive output. Diffuse previews include material color and AO. Roughness is read but has no shading effect until specular is added. Painter display transforms still apply." }
uniform int debug_output;

struct SurfaceData
{
    vec3 baseColor;
    vec3 normalWS;
    vec3 emissive;
    float roughness;
    float metallic;
    float ao;
    float opacity;
};

struct DiffuseData
{
    vec3 npr;
    vec3 pbr;
    float pbrWeight;
    vec3 color;
};

vec3 SafeNormalize(vec3 value)
{
    float lengthSquared = dot(value, value);
    return lengthSquared > 1e-12
        ? value * inversesqrt(lengthSquared)
        : vec3(0.0, 0.0, 1.0);
}

float ComputeRampLighting(vec3 normal, vec3 lightDir)
{
    return clamp(dot(SafeNormalize(normal), SafeNormalize(lightDir)), 0.0, 1.0);
}

float AdjustRampCoordinate(float lightValue, float offset, float contrast)
{
    return clamp((lightValue - 0.5) * contrast + 0.5 + offset, 0.0, 1.0);
}

vec3 ComposeRampColor(vec3 baseColor, vec3 rampColor, float strength, float intensity)
{
    return baseColor * mix(vec3(1.0), rampColor, strength) * intensity;
}

float GetDiffusePBRWeight(int mode, float rampValue)
{
    if (mode == 1) return 1.0;
    if (mode == 2) return clamp(rampValue, 0.0, 1.0);
    return 0.0;
}

vec4 SampleRampTexture(sampler2D rampTexture, float value, int filtering)
{
    ivec2 size = max(textureSize(rampTexture, 0), ivec2(1));
    float x = clamp(value, 0.0, 1.0);

    if (filtering == 1) {

        ivec2 pixel = min(ivec2(x * float(size.x), 0.5 * float(size.y)), size - 1);
        return texelFetch(rampTexture, pixel, 0);
    }

    vec2 pixel = vec2(x * float(size.x - 1), 0.5 * float(size.y - 1));
    ivec2 lo = ivec2(floor(pixel));
    ivec2 hi = min(lo + 1, size - 1);
    vec2 blend = fract(pixel);
    vec4 bottom = mix(texelFetch(rampTexture, lo, 0),
                      texelFetch(rampTexture, ivec2(hi.x, lo.y), 0), blend.x);
    vec4 top = mix(texelFetch(rampTexture, ivec2(lo.x, hi.y), 0),
                   texelFetch(rampTexture, hi, 0), blend.x);
    return mix(bottom, top, blend.y);
}

vec4 EvaluateRamp(float value)
{
    return SampleRampTexture(ramp_texture, value, ramp_filtering);
}

vec3 GetLightDirectionWS()
{
    vec3 direction = SafeNormalize(light_direction);

    return SafeNormalize(transpose(environment_matrix) * direction);
}

SurfaceData ReadSurface(V2F inputs)
{
    SurfaceData surface;
    surface.baseColor = getBaseColor(basecolor_texture, inputs.sparse_coord);
    surface.normalWS = SafeNormalize(computeWSNormal(inputs.sparse_coord,
                                    inputs.tangent, inputs.bitangent, inputs.normal));
    surface.roughness = clamp(getRoughness(roughness_texture, inputs.sparse_coord), 0.0, 1.0);
    surface.metallic = clamp(getMetallic(metallic_texture, inputs.sparse_coord), 0.0, 1.0);
    surface.ao = clamp(getAO(inputs.sparse_coord), 0.0, 1.0);
    surface.emissive = pbrComputeEmissive(emissive_tex, inputs.sparse_coord);
    surface.opacity = clamp(getOpacity(opacity_texture, inputs.sparse_coord), 0.0, 1.0);
    return surface;
}

DiffuseData EvaluateDiffuse(SurfaceData surface, vec3 rampColor, float rampValue)
{

    vec3 diffuseColor = generateDiffuseColor(surface.baseColor, surface.metallic);
    DiffuseData diffuse;
    diffuse.npr = surface.ao * ComposeRampColor(diffuseColor, rampColor,
                                               shadow_strength, light_intensity);

    diffuse.pbr = surface.ao * diffuseColor * envIrradiance(surface.normalWS);
    diffuse.pbrWeight = GetDiffusePBRWeight(diffuse_mode, rampValue);
    diffuse.color = mix(diffuse.npr, diffuse.pbr, diffuse.pbrWeight);
    return diffuse;
}

void WritePainterOutput(SurfaceData surface, vec3 diffuseColor, bool diagnostic)
{

    albedoOutput(vec3(1.0));
    diffuseShadingOutput(diffuseColor);
    emissiveColorOutput(diagnostic ? vec3(0.0) : surface.emissive);

    alphaOutput(diagnostic ? 1.0 : surface.opacity);
}

vec3 SelectPreviewColor(int mode, SurfaceData surface, DiffuseData diffuse,
                       float lightingValue, float rampValue, vec3 rampColor)
{
    if (mode == 1) return vec3(lightingValue);
    if (mode == 2) return vec3(rampValue);
    if (mode == 3) return rampColor;
    if (mode == 4) return surface.baseColor;
    if (mode == 5) return surface.normalWS * 0.5 + 0.5;
    if (mode == 6) return vec3(surface.roughness);
    if (mode == 7) return vec3(surface.metallic);
    if (mode == 8) return vec3(surface.ao);
    if (mode == 9) return surface.emissive;
    if (mode == 10) return vec3(surface.opacity);
    if (mode == 11) return diffuse.npr;
    if (mode == 12) return diffuse.pbr;
    if (mode == 13) return vec3(diffuse.pbrWeight);
    return diffuse.color;
}

void shade(V2F inputs)
{
    SurfaceData surface = ReadSurface(inputs);
    float lightingValue = ComputeRampLighting(surface.normalWS, GetLightDirectionWS());
    float rampValue = AdjustRampCoordinate(lightingValue, ramp_offset, ramp_contrast);
    vec4 ramp = EvaluateRamp(rampValue);
    DiffuseData diffuse = EvaluateDiffuse(surface, ramp.rgb, rampValue);

    vec3 previewColor = SelectPreviewColor(debug_output, surface, diffuse,
                                          lightingValue, rampValue, ramp.rgb);
    WritePainterOutput(surface, previewColor, debug_output != 0);
}
