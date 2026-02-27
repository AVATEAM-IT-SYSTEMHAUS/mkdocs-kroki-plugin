# Data Visualization & Signals

Diagram types for data visualization, charts, digital timing diagrams, and byte-level data formats.

## Vega

Vega is a declarative format for creating interactive visualizations.

### Bar Chart

```vega
{
  "$schema": "https://vega.github.io/schema/vega/v5.json",
  "width": 400,
  "height": 200,
  "padding": 5,
  "data": [
    {
      "name": "table",
      "values": [
        {"category": "Q1", "amount": 28},
        {"category": "Q2", "amount": 55},
        {"category": "Q3", "amount": 43},
        {"category": "Q4", "amount": 91}
      ]
    }
  ],
  "scales": [
    {
      "name": "xscale",
      "type": "band",
      "domain": {"data": "table", "field": "category"},
      "range": "width",
      "padding": 0.05
    },
    {
      "name": "yscale",
      "domain": {"data": "table", "field": "amount"},
      "nice": true,
      "range": "height"
    }
  ],
  "axes": [
    {"orient": "bottom", "scale": "xscale"},
    {"orient": "left", "scale": "yscale"}
  ],
  "marks": [
    {
      "type": "rect",
      "from": {"data": "table"},
      "encode": {
        "enter": {
          "x": {"scale": "xscale", "field": "category"},
          "width": {"scale": "xscale", "band": 1},
          "y": {"scale": "yscale", "field": "amount"},
          "y2": {"scale": "yscale", "value": 0}
        },
        "update": {
          "fill": {"value": "steelblue"}
        }
      }
    }
  ]
}
```

## Vega-Lite

Vega-Lite is a higher-level grammar for rapid visualization.

### Scatter Plot

```vegalite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "Quarterly revenue by region",
  "data": {
    "values": [
      {"month": "Jan", "sales": 28, "region": "North"},
      {"month": "Feb", "sales": 55, "region": "North"},
      {"month": "Mar", "sales": 43, "region": "North"},
      {"month": "Apr", "sales": 91, "region": "North"},
      {"month": "Jan", "sales": 81, "region": "South"},
      {"month": "Feb", "sales": 53, "region": "South"},
      {"month": "Mar", "sales": 19, "region": "South"},
      {"month": "Apr", "sales": 87, "region": "South"}
    ]
  },
  "mark": "point",
  "encoding": {
    "x": {"field": "month", "type": "nominal", "title": "Month"},
    "y": {"field": "sales", "type": "quantitative", "title": "Sales"},
    "color": {"field": "region", "type": "nominal"},
    "size": {"field": "sales", "type": "quantitative"}
  }
}
```

### Bar Chart

```vegalite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "Programming language popularity",
  "data": {
    "values": [
      {"language": "Python", "users": 48},
      {"language": "JavaScript", "users": 38},
      {"language": "Java", "users": 31},
      {"language": "C++", "users": 24},
      {"language": "Go", "users": 14},
      {"language": "Rust", "users": 10}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "language", "type": "nominal", "sort": "-y", "title": "Language"},
    "y": {"field": "users", "type": "quantitative", "title": "Users (millions)"},
    "color": {"field": "language", "type": "nominal", "legend": null}
  }
}
```

## WaveDrom

WaveDrom renders digital timing diagrams from JSON descriptions.

### SPI Communication

```wavedrom
{ "signal": [
  { "name": "CLK",  "wave": "p........" },
  { "name": "MOSI", "wave": "x.345678x", "data": ["D7","D6","D5","D4","D3","D2","D1","D0"] },
  { "name": "MISO", "wave": "x.345678x", "data": ["Q7","Q6","Q5","Q4","Q3","Q2","Q1","Q0"] },
  { "name": "SS",   "wave": "10.......1" }
]}
```

### Memory Read Cycle

```wavedrom
{ "signal": [
  { "name": "clk",   "wave": "p.....|..." },
  { "name": "addr",  "wave": "x.3...|.x.", "data": ["A"] },
  { "name": "wr_en", "wave": "0.....|..." },
  { "name": "rd_en", "wave": "0.1...|.0." },
  { "name": "data",  "wave": "z.....|.4.", "data": ["D"] },
  { "name": "ack",   "wave": "0.....|.10" }
],
  "head": { "text": "Memory Read Cycle" }
}
```

## Bytefield

Bytefield renders byte-level protocol and data structure diagrams using a Clojure-style DSL.

### IPv4 Header

```bytefield
(defattrs :bg-green {:fill "#a0ffa0"})
(defattrs :bg-yellow {:fill "#ffffa0"})
(defattrs :bg-pink {:fill "#ffb0a0"})
(defattrs :bg-cyan {:fill "#a0fafa"})
(defattrs :bg-purple {:fill "#e4b5f7"})

(defn draw-group-label-header
  "Creates a small borderless box used to draw the textual label headers
  used below the byte labels for remotedb message diagrams.
  Arguments are the number of columns to span and the text of the
  label."
  [span label]
  (draw-box (text label [:math {:font-size 12}]) {:span    span
                                                  :borders #{}
                                                  :height  14}))

(defn draw-remotedb-header
  "Generates the byte and field labels and standard header fields of a
  request or response message for the remotedb database server with
  the specified kind and args values."
  [kind args]
  (draw-column-headers)
  (draw-group-label-header 5 "start")
  (draw-group-label-header 5 "TxID")
  (draw-group-label-header 3 "type")
  (draw-group-label-header 2 "args")
  (draw-group-label-header 1 "tags")
  (next-row 18)

  (draw-box 0x11 :bg-green)
  (draw-box 0x872349ae [{:span 4} :bg-green])
  (draw-box 0x11 :bg-yellow)
  (draw-box (text "TxID" :math) [{:span 4} :bg-yellow])
  (draw-box 0x10 :bg-pink)
  (draw-box (hex-text kind 4 :bold) [{:span 2} :bg-pink])
  (draw-box 0x0f :bg-cyan)
  (draw-box (hex-text args 2 :bold) :bg-cyan)
  (draw-box 0x14 :bg-purple)

  (draw-box (text "0000000c" :hex [[:plain {:font-weight "light" :font-size 16}] " (12)"])
            [{:span 4} :bg-purple])
  (draw-box (hex-text 6 2 :bold) [:box-first :bg-purple])
  (doseq [val [6 6 3 6 6 6 6 3]]
    (draw-box (hex-text val 2 :bold) [:box-related :bg-purple]))
  (doseq [val [0 0]]
    (draw-box val [:box-related :bg-purple]))
  (draw-box 0 [:box-last :bg-purple]))

(draw-remotedb-header 0x4702 9)

(draw-box 0x11)
(draw-box 0x2104 {:span 4})
(draw-box 0x11)
(draw-box 0 {:span 4})
(draw-box 0x11)
(draw-box (text "length" [:math] [:sub 1]) {:span 4})
(draw-box 0x14)

(draw-box (text "length" [:math] [:sub 1]) {:span 4})
(draw-gap "Cue and loop point bytes")

(draw-box nil :box-below)
(draw-box 0x11)
(draw-box 0x36 {:span 4})
(draw-box 0x11)
(draw-box (text "num" [:math] [:sub "hot"]) {:span 4})
(draw-box 0x11)
(draw-box (text "num" [:math] [:sub "cue"]) {:span 4})

(draw-box 0x11)
(draw-box (text "length" [:math] [:sub 2]) {:span 4})
(draw-box 0x14)
(draw-box (text "length" [:math] [:sub 2]) {:span 4})
(draw-gap "Unknown bytes" {:min-label-columns 6})
(draw-bottom)

```
