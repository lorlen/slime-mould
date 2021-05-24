#version 460 core

in vec2 in_position;
in vec2 in_texcoord_0;

out vec2 frag_texcoord;

void main() {
    frag_texcoord = in_texcoord_0;
    gl_Position = vec4(in_position, 0.0, 1.0);
}
