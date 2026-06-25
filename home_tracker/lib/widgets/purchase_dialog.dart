import 'package:flutter/material.dart';
import '../data/storage.dart';
import '../models/models.dart';

class PurchaseDialog extends StatefulWidget {
  final Purchase? purchase;
  const PurchaseDialog({super.key, this.purchase});
  @override
  State<PurchaseDialog> createState() => _PurchaseDialogState();
}

class _PurchaseDialogState extends State<PurchaseDialog> {
  late TextEditingController _titleCtrl;
  late TextEditingController _amountCtrl;
  late TextEditingController _commentCtrl;
  late String _type;
  late String _category;
  late String _date;
  late String _purchaseStatus;

  String _today() {
    final n = DateTime.now();
    return '${n.year}-${n.month.toString().padLeft(2, '0')}-${n.day.toString().padLeft(2, '0')}';
  }

  @override
  void initState() {
    super.initState();
    final p = widget.purchase;
    _titleCtrl = TextEditingController(text: p?.title ?? '');
    _amountCtrl = TextEditingController(text: p != null && p.amount > 0 ? p.amount.toStringAsFixed(0) : '');
    _commentCtrl = TextEditingController(text: p?.comment ?? '');
    _type = p?.type ?? 'regular';
    _category = p?.category ?? 'Продукты';
    _date = p?.date ?? _today();
    _purchaseStatus = p?.purchaseStatus ?? 'planned';
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    _amountCtrl.dispose();
    _commentCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final categories = ['Продукты', 'Хозяйственные', 'Ремонт', 'Одежда', 'Техника', 'Другое'];
    return AlertDialog(
      title: Text(widget.purchase == null ? 'Новая покупка' : 'Редактировать покупку'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: _titleCtrl, decoration: const InputDecoration(labelText: 'Название', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _purchaseStatus,
              items: const [
                DropdownMenuItem(value: 'planned', child: Text('📋 Запланировано')),
                DropdownMenuItem(value: 'purchased', child: Text('✅ Куплено')),
              ],
              onChanged: (v) => setState(() => _purchaseStatus = v ?? _purchaseStatus),
              decoration: const InputDecoration(labelText: 'Статус', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _type,
              items: const [
                DropdownMenuItem(value: 'regular', child: Text('Повседневная')),
                DropdownMenuItem(value: 'large', child: Text('Крупная')),
              ],
              onChanged: (v) => setState(() => _type = v ?? _type),
              decoration: const InputDecoration(labelText: 'Тип', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _category,
              items: categories.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
              onChanged: (v) => setState(() => _category = v ?? _category),
              decoration: const InputDecoration(labelText: 'Категория товара', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 12),
            TextField(
              decoration: const InputDecoration(labelText: 'Дата', border: OutlineInputBorder()),
              readOnly: true,
              controller: TextEditingController(text: _date),
              onTap: () async {
                final d = await showDatePicker(
                  context: context,
                  initialDate: DateTime.tryParse(_date) ?? DateTime.now(),
                  firstDate: DateTime(2020),
                  lastDate: DateTime(2035),
                );
                if (d != null) setState(() => _date = '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}');
              },
            ),
            const SizedBox(height: 12),
            TextField(controller: _amountCtrl, decoration: const InputDecoration(labelText: 'Сумма (₽)', border: OutlineInputBorder()), keyboardType: TextInputType.number),
            const SizedBox(height: 12),
            TextField(controller: _commentCtrl, decoration: const InputDecoration(labelText: 'Комментарий', border: OutlineInputBorder())),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Отмена')),
        FilledButton(
          onPressed: () {
            final title = _titleCtrl.text.trim();
            if (title.isEmpty) return;
            final purchase = Purchase(
              id: widget.purchase?.id ?? Storage.genId(),
              title: title,
              type: _type,
              category: _category,
              date: _date,
              amount: double.tryParse(_amountCtrl.text) ?? 0,
              comment: _commentCtrl.text.trim(),
              purchaseStatus: _purchaseStatus,
            );
            Navigator.pop(context, purchase);
          },
          child: const Text('Сохранить'),
        ),
      ],
    );
  }
}
