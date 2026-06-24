import 'package:flutter/material.dart';
import '../models/models.dart';
import '../data/storage.dart';

Future<Chore?> showChoreDialog(BuildContext context, {
  required List<String> categories,
  Chore? chore,
  VoidCallback? onManageCategories,
}) {
  return showDialog<Chore>(
    context: context,
    builder: (_) => ChoreDialog(
      chore: chore,
      categories: categories,
      onManageCategories: onManageCategories,
    ),
  );
}

class ChoreDialog extends StatefulWidget {
  final Chore? chore;
  final List<String> categories;
  final VoidCallback? onManageCategories;

  const ChoreDialog({
    super.key,
    this.chore,
    required this.categories,
    this.onManageCategories,
  });

  @override
  State<ChoreDialog> createState() => _ChoreDialogState();
}

class _ChoreDialogState extends State<ChoreDialog> {
  late TextEditingController _titleCtrl;
  late String _category;
  late String _assignee;
  late String _date;
  late String _priority;

  @override
  void initState() {
    super.initState();
    final c = widget.chore;
    _titleCtrl = TextEditingController(text: c?.title ?? '');
    _category = c?.category ?? (widget.categories.isNotEmpty ? widget.categories.first : '');
    _assignee = c?.assignee ?? 'Я';
    _date = c?.date ?? _today();
    _priority = c?.priority ?? 'Средний';
  }

  String _today() {
    final n = DateTime.now();
    return '${n.year}-${n.month.toString().padLeft(2, '0')}-${n.day.toString().padLeft(2, '0')}';
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.chore == null ? 'Новое дело' : 'Редактировать дело'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _titleCtrl,
              decoration: const InputDecoration(labelText: 'Название', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _category,
              items: widget.categories.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
              onChanged: (v) => setState(() => _category = v ?? _category),
              decoration: InputDecoration(
                labelText: 'Категория',
                border: const OutlineInputBorder(),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.settings, size: 18),
                  onPressed: widget.onManageCategories,
                ),
              ),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _assignee,
              items: const ['Я', 'Муж', 'Оба'].map((a) => DropdownMenuItem(value: a, child: Text(a))).toList(),
              onChanged: (v) => setState(() => _assignee = v ?? _assignee),
              decoration: const InputDecoration(labelText: 'Ответственный', border: OutlineInputBorder()),
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
            DropdownButtonFormField<String>(
              value: _priority,
              items: const ['Низкий', 'Средний', 'Высокий'].map((p) => DropdownMenuItem(value: p, child: Text(p))).toList(),
              onChanged: (v) => setState(() => _priority = v ?? _priority),
              decoration: const InputDecoration(labelText: 'Приоритет', border: OutlineInputBorder()),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Отмена')),
        FilledButton(
          onPressed: () {
            final title = _titleCtrl.text.trim();
            if (title.isEmpty) return;
            final chore = Chore(
              id: widget.chore?.id ?? Storage.genId(),
              title: title,
              category: _category,
              assignee: _assignee,
              date: _date,
              priority: _priority,
              done: widget.chore?.done ?? false,
            );
            Navigator.pop(context, chore);
          },
          child: const Text('Сохранить'),
        ),
      ],
    );
  }
}
