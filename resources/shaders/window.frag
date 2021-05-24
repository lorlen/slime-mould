#version 460 core

in vec2 frag_texcoord;

out vec4 color;

uniform sampler2D tex_sampler;

void main() {
    color = texture(tex_sampler, frag_texcoord);
}
