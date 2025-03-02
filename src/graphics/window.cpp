#include "window.h"

using namespace ws;

window::window(std::string_view title, int width, int height) {
  ray::InitWindow(width, height, title.data());
}

window::~window() {
  ray::CloseWindow();
}
