#ifndef DRAW_H
#define DRAW_H

#include "src/utils/common.h"

namespace ws {

using location = ray::Vector2;

class renderer {
  // Current color to draw.
  ray::Color color;
  std::map<std::string, ray::Texture2D> card_cache;

public:
  void draw_text(std::string_view text, location loc);
  void draw_image(const std::string &filename, location loc);
};

struct render_context {
  render_context(ray::Color bgcolor = BLACK);
  ~render_context();
};

}

#endif
