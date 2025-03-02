#include "src/graphics/window.h"
#include "src/graphics/draw.h"

int main() {
  ws::window win("Windspeak", 1280, 960);

  ws::renderer renderer;
  win.event_loop([&]() {
    ws::render_context _ctx(/*background_color=*/{ 235, 236, 213, 255 });
    renderer.draw_image("assets/cards/see-through.png", { 100, 200 });
  });
}
