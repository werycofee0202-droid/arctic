export const MAX_SIZE_MB = 25;

export const ALLOWED = {
  project:     { exts: [".pdf", ".docx"], mimes: ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"] },
  presentation:{ exts: [".pdf", ".pptx"], mimes: ["application/pdf", "application/vnd.openxmlformats-officedocument.presentationml.presentation"] },
  video:       { exts: [".mp4", ".mov"], mimes: ["video/mp4", "video/quicktime"] },
};

export function validateFile(file, kind) {
  if (!file) return "Файл не выбран";
  const rule = ALLOWED[kind];
  const name = file.name.toLowerCase();
  const okExt = rule.exts.some(e => name.endsWith(e));
  const okMime = !file.type || rule.mimes.includes(file.type);
  if (!okExt || !okMime) return `Недопустимый формат. Разрешено: ${rule.exts.join(", ")}`;
  if (file.size > MAX_SIZE_MB * 1024 * 1024) return `Файл больше ${MAX_SIZE_MB} МБ`;
  return null;
}

export function validateVideoLink(url) {
  if (!url) return null; // необязательное
  try {
    const u = new URL(url);
    return ["http:", "https:"].includes(u.protocol) ? null : "Ссылка должна начинаться с http(s)://";
  } catch {
    return "Некорректная ссылка";
  }
}