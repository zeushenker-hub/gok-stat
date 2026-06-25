import 'package:flutter/material.dart';
import '../data/storage.dart';
import '../data/product_catalog.dart';
import '../models/models.dart';

class PurchaseDialog extends StatefulWidget {
  final Purchase? purchase;
  const PurchaseDialog({super.key, this.purchase});
  @override
  State<PurchaseDialog> createState() => _PurchaseDialogState();
}

class _PurchaseDialogState extends State<PurchaseDialog> {
  final _titleCtrl = TextEditingController();
  late TextEditingController _amountCtrl;
  late TextEditingController _commentCtrl;
  late TextEditingController _quantityCtrl;
  late String _type;
  late String _category;
  late String _date;
  late String _purchaseStatus;
  late String _unit;
  late String _store;

  List<String> _allNames = [];
  static const _units = ['г', 'кг', 'мл', 'л', 'шт'];
  static const _stores = ['Гуливер', 'Рынок', 'Пятерочка', 'Чижик', 'Перекресток', 'Магнит', 'Ашан', 'Другое'];

  String _today() {
    final n = DateTime.now();
    return '${n.year}-${n.month.toString().padLeft(2, '0')}-${n.day.toString().padLeft(2, '0')}';
  }

  @override
  void initState() {
    super.initState();
    _loadNames();
    final p = widget.purchase;
    _titleCtrl.text = p?.title ?? '';
    _amountCtrl = TextEditingController(text: p != null && p.amount > 0 ? p.amount.toStringAsFixed(0) : '');
    _commentCtrl = TextEditingController(text: p?.comment ?? '');
    _quantityCtrl = TextEditingController(text: p != null && p.quantity != 1.0 ? p.quantity.toString() : '');
    _type = p?.type ?? 'regular';
    _category = p?.category ?? 'Продукты';
    _date = p?.date ?? _today();
    _purchaseStatus = p?.purchaseStatus ?? 'planned';
    _unit = p?.unit ?? 'шт';
    _store = p?.store ?? '';
  }

  Future<void> _loadNames() async {
    final fromCatalog = allCatalogNames();
    final history = <String>{};
    for (final p in await Storage.loadPurchases()) {
      if (p.title.isNotEmpty) history.add(p.title);
    }
    _allNames = {...fromCatalog, ...history}.toList()..sort();
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    _amountCtrl.dispose();
    _commentCtrl.dispose();
    _quantityCtrl.dispose();
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
            Autocomplete<String>(
              optionsBuilder: (textEditingValue) {
                if (textEditingValue.text.isEmpty) return [];
                return _allNames.where((name) =>
                    name.toLowerCase().contains(textEditingValue.text.toLowerCase()));
              },
              fieldViewBuilder: (context, controller, focusNode, onSubmitted) {
                // Синхронизируем с _titleCtrl
                if (controller.text != _titleCtrl.text) {
                  _titleCtrl.text = controller.text;
                }
                return TextField(
                  controller: controller,
                  focusNode: focusNode,
                  decoration: const InputDecoration(labelText: 'Название', border: OutlineInputBorder()),
                );
              },
              onSelected: (value) {
                _titleCtrl.text = value;
              },
            ),
            const SizedBox(height: 10),
            DropdownButtonFormField<String>(
              value: _purchaseStatus,
              items: const [
                DropdownMenuItem(value: 'planned', child: Text('📋 Запланировано')),
                DropdownMenuItem(value: 'purchased', child: Text('✅ Куплено')),
              ],
              onChanged: (v) => setState(() => _purchaseStatus = v ?? _purchaseStatus),
              decoration: const InputDecoration(labelText: 'Статус', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 10),
            DropdownButtonFormField<String>(
              value: _type,
              items: const [
                DropdownMenuItem(value: 'regular', child: Text('Повседневная')),
                DropdownMenuItem(value: 'large', child: Text('Крупная')),
              ],
              onChanged: (v) => setState(() => _type = v ?? _type),
              decoration: const InputDecoration(labelText: 'Тип', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 10),
            DropdownButtonFormField<String>(
              value: _category,
              items: categories.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
              onChanged: (v) => setState(() => _category = v ?? _category),
              decoration: const InputDecoration(labelText: 'Категория', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 10),
            DropdownButtonFormField<String>(
              value: _store.isEmpty ? null : _store,
              items: [
                const DropdownMenuItem(value: '', child: Text('Не выбран')),
                ..._stores.map((s) => DropdownMenuItem(value: s, child: Text(s))),
              ],
              onChanged: (v) => setState(() => _store = v ?? ''),
              decoration: const InputDecoration(labelText: 'Магазин', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 10),
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
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  flex: 2,
                  child: TextField(
                    controller: _quantityCtrl,
                    decoration: const InputDecoration(labelText: 'Количество', border: OutlineInputBorder()),
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _unit,
                    items: _units.map((u) => DropdownMenuItem(value: u, child: Text(u))).toList(),
                    onChanged: (v) => setState(() => _unit = v ?? _unit),
                    decoration: const InputDecoration(labelText: 'Ед.', border: OutlineInputBorder(), isDense: true),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _amountCtrl,
              decoration: const InputDecoration(labelText: 'Цена (₽)', border: OutlineInputBorder()),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 10),
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
              quantity: double.tryParse(_quantityCtrl.text) ?? 1.0,
              unit: _unit,
              store: _store,
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
