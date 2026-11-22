-- Cells of a pipe table have to be written on a single source line, so the
-- multi-line cells in this manuscript are authored with <br>. Pandoc keeps that
-- as raw HTML and the docx writer discards raw HTML, which glues the lines
-- together in Word. Turning it into a real line break keeps both outputs equal.
function RawInline(el)
  if el.format:match("html") and el.text:match("^%s*<[bB][rR]%s*/?>%s*$") then
    return pandoc.LineBreak()
  end
end
