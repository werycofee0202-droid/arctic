import jsPDF from "jspdf";
import QRCode from "qrcode";

export async function generateCertificate({
  participantName,
  region,
  school,
  score,
  total,
  certId,
  date = new Date().toLocaleDateString("ru-RU"),
}) {
  const doc = new jsPDF({ orientation: "landscape", unit: "mm", format: "a4" });

  const W = doc.internal.pageSize.getWidth();
  const H = doc.internal.pageSize.getHeight();

  // Фон
  doc.setFillColor(8, 20, 38);
  doc.rect(0, 0, W, H, "F");

  // Рамка
  doc.setDrawColor(79, 209, 197);
  doc.setLineWidth(1.2);
  doc.rect(10, 10, W - 20, H - 20);

  // Заголовок
  doc.setTextColor(234, 242, 255);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(14);
  doc.text("КОНКУРС «УДИВИТЕЛЬНАЯ И НЕИЗВЕДАННАЯ АРКТИКА»", W / 2, 30, { align: "center" });

  doc.setFontSize(26);
  doc.setTextColor(79, 209, 197);
  doc.text("СЕРТИФИКАТ УЧАСТНИКА", W / 2, 55, { align: "center" });

  doc.setFontSize(12);
  doc.setTextColor(157, 180, 208);
  doc.text("I этап • Тестирование", W / 2, 66, { align: "center" });

  // ФИО
  doc.setTextColor(234, 242, 255);
  doc.setFontSize(22);
  doc.setFont("helvetica", "bold");
  doc.text(participantName, W / 2, 95, { align: "center" });

  // Мета
  doc.setFont("helvetica", "normal");
  doc.setFontSize(12);
  doc.setTextColor(157, 180, 208);
  doc.text(`${region} • ${school}`, W / 2, 105, { align: "center" });

  // Результат
  doc.setFontSize(15);
  doc.setTextColor(79, 209, 197);
  doc.text(`Результат: ${score} из ${total}`, W / 2, 125, { align: "center" });

  // Номер и дата
  doc.setFontSize(10);
  doc.setTextColor(157, 180, 208);
  doc.text(`№ ${certId}`, 20, H - 20);
  doc.text(`Дата выдачи: ${date}`, W - 20, H - 20, { align: "right" });

  // QR-код (ссылка на проверку)
  const verifyUrl = `https://arctic-contest.ru/verify/${certId}`;
  const qrDataUrl = await QRCode.toDataURL(verifyUrl, {
    color: { dark: "#4fd1c5", light: "#081426" },
    margin: 1,
    width: 220,
  });
  doc.addImage(qrDataUrl, "PNG", W - 55, H - 70, 38, 38);

  doc.save(`Сертификат_${certId}.pdf`);
}

export function makeCertId() {
  const stamp = Date.now().toString(36).toUpperCase();
  const rand = Math.random().toString(36).slice(2, 7).toUpperCase();
  return `ARK-${stamp}-${rand}`;
}