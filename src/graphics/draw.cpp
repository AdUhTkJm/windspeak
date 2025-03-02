#include "draw.h"

using namespace ws;

render_context::render_context(ray::Color bgcolor) {
  ray::BeginDrawing();
  ray::ClearBackground(bgcolor);
}

render_context::~render_context() {
  ray::EndDrawing();
}

void renderer::draw_text(std::string_view text, location loc) {
  auto [x, y] = loc;
  ray::DrawText(text.data(), x, y, 12, color);
}

void renderer::draw_image(const std::string &filename, location loc) {
  if (!card_cache.contains(filename)) {
    std::cerr << std::format("loaded {}\n", filename);
    card_cache[filename] = ray::LoadTexture(filename.data());
  }

  ray::Texture2D texture = card_cache[filename];
  ray::DrawTexture(texture, loc.x, loc.y, WHITE);
}
