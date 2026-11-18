// Inspect one Illustrator file and export every artboard as PNG.
// Runs inside Adobe Illustrator (ExtendScript). Launched by run_illustrator.ps1
// (Windows) or osascript (macOS) with arguments:
//   arguments[0]  absolute path of the .ai file
//   arguments[1]  absolute output folder (must exist)
//   arguments[2]  PNG scale percent (optional, default 100 = 1px per point)
//
// Writes <out>/<stem>-ai-ab01.png ... and <out>/<stem>.illustrator.json.
// Never saves the document. If the file was already open, it is left open and
// untouched apart from the active artboard; otherwise it is closed unsaved.

(function (args) {
  var inPath = args[0], outDir = args[1];
  var scale = Number(args[2] || 100);
  if (!inPath || !outDir) return '{"error":"usage: <file.ai> <out dir> [scale]"}';

  function esc(s) {
    return String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"')
      .replace(/\n/g, "\\n").replace(/\r/g, "\\n").replace(/\t/g, " ")
      .replace(/[\x00-\x1f]/g, "");
  }
  function json(v) {
    if (v === null || v === undefined) return "null";
    if (typeof v === "number" || typeof v === "boolean") return String(v);
    if (typeof v === "string") return '"' + esc(v) + '"';
    var i, a = [];
    if (v instanceof Array) { for (i = 0; i < v.length; i++) a.push(json(v[i])); return "[" + a.join(",") + "]"; }
    for (i in v) if (v.hasOwnProperty(i)) a.push('"' + esc(i) + '":' + json(v[i]));
    return "{" + a.join(",") + "}";
  }

  var file = new File(inPath);
  if (!file.exists) return json({ error: "file not found", file: inPath });

  var prevLevel = app.userInteractionLevel;
  app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

  var doc = null, wasOpen = false, i, j;
  for (i = 0; i < app.documents.length; i++) {
    if (app.documents[i].fullName.fsName == file.fsName) { doc = app.documents[i]; wasOpen = true; break; }
  }
  var r = { file: file.fsName, already_open: wasOpen };
  try {
    if (!doc) doc = app.open(file);
    var prevAb = doc.artboards.getActiveArtboardIndex();

    r.color_space = String(doc.documentColorSpace).replace("DocumentColorSpace.", "");
    r.artboards = [];
    for (i = 0; i < doc.artboards.length; i++) {
      var b = doc.artboards[i].artboardRect;
      r.artboards.push({ index: i + 1, name: doc.artboards[i].name,
        w_mm: Math.round((b[2] - b[0]) * 25.4 / 72 * 10) / 10,
        h_mm: Math.round((b[1] - b[3]) * 25.4 / 72 * 10) / 10 });
    }

    function layers(coll) {
      var out = [];
      for (var k = 0; k < coll.length; k++) {
        var L = coll[k];
        out.push({ name: L.name, visible: L.visible, locked: L.locked,
                   items: L.pageItems.length, sublayers: layers(L.layers) });
      }
      return out;
    }
    r.layers = layers(doc.layers);

    var fonts = {}, texts = [];
    for (i = 0; i < doc.textFrames.length; i++) {
      var tf = doc.textFrames[i];
      try {
        for (j = 0; j < tf.paragraphs.length; j++) {
          try { fonts[tf.paragraphs[j].characterAttributes.textFont.name] = 1; } catch (e1) {}
        }
      } catch (e2) {}
      try { if (tf.contents) texts.push(tf.contents.substring(0, 300)); } catch (e3) {}
    }
    r.fonts = []; for (i in fonts) if (fonts.hasOwnProperty(i)) r.fonts.push(i);
    r.text = texts;

    r.spot_colors = [];
    for (i = 0; i < doc.spots.length; i++) {
      var sn = doc.spots[i].name;
      if (sn != "[Registration]") r.spot_colors.push(sn);
    }
    r.swatch_count = doc.swatches.length;

    r.links = []; r.broken_links = 0;
    for (i = 0; i < doc.placedItems.length; i++) {
      var link;
      try { link = { path: doc.placedItems[i].file.fsName, ok: doc.placedItems[i].file.exists }; }
      catch (e4) { link = { path: null, ok: false }; }
      if (!link.ok) r.broken_links++;
      r.links.push(link);
    }
    r.embedded_rasters = doc.rasterItems.length;

    var stem = file.name.replace(/\.ai$/i, "").replace(/[^A-Za-z0-9._-]+/g, "-");
    var opt = new ExportOptionsPNG24();
    opt.artBoardClipping = true; opt.antiAliasing = true; opt.transparency = true;
    opt.horizontalScale = scale; opt.verticalScale = scale;
    r.exports = [];
    for (i = 0; i < doc.artboards.length; i++) {
      doc.artboards.setActiveArtboardIndex(i);
      var name = stem + "-ai-ab" + (i < 9 ? "0" : "") + (i + 1) + ".png";
      doc.exportFile(new File(outDir + "/" + name), ExportType.PNG24, opt);
      r.exports.push(name);
    }
    doc.artboards.setActiveArtboardIndex(prevAb);

    var jf = new File(outDir + "/" + stem + ".illustrator.json");
    jf.encoding = "UTF-8"; jf.open("w"); jf.write(json(r)); jf.close();
  } catch (e) {
    r.error = String(e);
  } finally {
    if (doc && !wasOpen) doc.close(SaveOptions.DONOTSAVECHANGES);
    app.userInteractionLevel = prevLevel;
  }
  return json({ file: r.file, artboards: r.artboards ? r.artboards.length : 0,
                exports: r.exports ? r.exports.length : 0, fonts: r.fonts, broken_links: r.broken_links,
                already_open: wasOpen, error: r.error || null });
})(arguments);
