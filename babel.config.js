const presets = [
  ["@babel/env", {
    targets: {
      browsers: ["last 2 versions", "ie >= 7"]
    },
    // This prevents babel from adding "use strict" to the top of every file, since we're adding it within the app template.
    modules: "false",
    // Not sure what this is for exactly.
    useBuiltIns: "false"
  }]
];

module.exports = { presets };
