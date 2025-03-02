#ifndef WINDOW_H
#define WINDOW_H

#include "src/utils/common.h"

namespace ws {

class window {
public:
  window(std::string_view title, int width, int height);
  ~window();

  void event_loop(auto callback) {
    while (!ray::WindowShouldClose())
      callback();
  }
};

}

#endif
