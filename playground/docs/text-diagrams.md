# Text & ASCII Diagrams

These diagram types convert text-based or ASCII art input into polished SVG graphics.

## Ditaa

Ditaa interprets ASCII art and converts it into proper bitmap graphics.

### System Architecture

```ditaa
+--------+   +-------+    +-------+
|        +---+ ditaa |    |       |
|  Text  |   +-------+--->|diagram|
|Document|   |!magic!|    |       |
|     {d}|   |       |    |       |
+---+----+   +-------+    +-------+
    :                         ^
    |       Lots of work      |
    +-------------------------+
```

### Deployment Pipeline

```ditaa
  +----------+    +----------+    +----------+    +----------+
  |          |    |          |    |          |    |          |
  |  Commit  +--->+  Build   +--->+  Test    +--->+  Deploy  |
  |    {io}  |    |          |    |          |    |   {s}    |
  +----+-----+    +----+-----+    +----+-----+    +----+-----+
       |               |               |               |
       v               v               v               v
  +---------+    +---------+    +---------+    +---------+
  |  Git    |    | Artifact|    | Report  |    |  Prod   |
  |  Repo   |    | Storage |    |  cGRE   |    | Server  |
  |  {s}    |    |  {s}    |    |         |    |  {s}    |
  +---------+    +---------+    +---------+    +---------+
```

## Svgbob

Svgbob converts ASCII diagrams into SVG, rendering lines, arrows, and shapes with smooth curves.

### Network Flow

```svgbob
                          .-,(  ),-.
    .--.            .--,(          ),--.
   ( o  )          (      Internet      )
    `--'            `--,(          ),--'
     |                  `-.( ).-'
     |                      |
     v                      v
 .--------.          .----------.
 | Client |--------->| Firewall |
 '--------'          '----------'
                          |
                    .-----+-----.
                    |           |
                    v           v
              .--------. .---------.
              | Web 01 | | Web 02  |
              '--------' '---------'
                    |           |
                    '-----+-----'
                          |
                          v
                    .----------.
                    | Database |
                    '----------'
```

### Simple Circuit

```svgbob
     +10V
      |
      |
     .-.
     | | 4.7k
     | |
     '-'
      |
      +------+-------o Vout
      |      |
     .-.    ===  100n
     | |    ---
     | | 10k|
     '-'     |
      |      |
      +------+
      |
     GND
```

## Pikchr

Pikchr is a PIC-like diagram language for creating clean technical diagrams.

### Data Processing Pipeline

```pikchr
arrow right 200% "Markdown" "Source"
box rad 10px "Kroki" "Server" fit
arrow right 200% "SVG" "Output"
arrow <-> down 70% from last box.s
box same "googlechart.com" fit
```
