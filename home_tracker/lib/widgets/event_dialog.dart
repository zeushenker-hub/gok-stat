import 'package:flutter/material.dart';
import '../data/storage.dart';
import '../models/models.dart';

class EventDialog extends StatefulWidget {
  final FamilyEvent? event;
  const EventDialog({super.key, this.event});
  @override
  State<EventDialog> createState() => _EventDialogState();
}

class _EventDialogState extends State<EventDialog> {
  late TextEditingController _titleCtrl;
  late TextEditingController _placeCtrl;
  late TextEditingController _commentCtrl;
  late String _type;
  late String _date;
  late String _time;

  @override
  void initState() {
    super.initState();
    final e = widget.event;
    _titleCtrl = TextEditingController(text: e?.title ?? '');
    _placeCtrl = TextEditingController(text: e?.place ?? '');
    _commentCtrl = TextEditingController(text: e?.comment ?? '');
    _type = e?.type ?? 'День рождения';
    _date = e?.date ?? '';
    _time = e?.time ?? '';
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    _placeCtrl.dispose();
    _commentCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.event == null ? 'Новое событие' : 'Редактировать событие'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: _titleCtrl, decoration: const InputDecoration(labelText: 'Название', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _type,
              items: const [
                DropdownMenuItem(value: 'День рождения', child: Text('🎂 День рождения')),
                DropdownMenuItem(value: 'Поездка', child: Text('✈️ Поездка')),
                DropdownMenuItem(value: 'Свадьба', child: Text('💍 Свадьба')),
                DropdownMenuItem(value: 'Юбилей', child: Text('🎉 Юбилей')),
                DropdownMenuItem(value: 'Праздник', child: Text('🎊 Праздник')),
                DropdownMenuItem(value: 'Встреча', child: Text('🤝 Встреча')),
                DropdownMenuItem(value: 'Другое', child: Text('📌 Другое')),
              ],
              onChanged: (v) => setState(() => _type = v ?? _type),
              decoration: const InputDecoration(labelText: 'Тип события', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
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
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    decoration: const InputDecoration(labelText: 'Время', border: OutlineInputBorder()),
                    readOnly: true,
                    controller: TextEditingController(text: _time),
                    onTap: () async {
                      final t = await showTimePicker(context: context, initialTime: TimeOfDay.now());
                      if (t != null) setState(() => _time = '${t.hour.toString().padLeft(2, '0')}:${t.minute.toString().padLeft(2, '0')}');
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            TextField(controller: _placeCtrl, decoration: const InputDecoration(labelText: 'Место', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            TextField(controller: _commentCtrl, decoration: const InputDecoration(labelText: 'Комментарий', border: OutlineInputBorder()), maxLines: 2),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Отмена')),
        FilledButton(
          onPressed: () {
            final title = _titleCtrl.text.trim();
            if (title.isEmpty) return;
            final event = FamilyEvent(
              id: widget.event?.id ?? Storage.genId(),
              title: title,
              type: _type,
              date: _date,
              time: _time,
              place: _placeCtrl.text.trim(),
              comment: _commentCtrl.text.trim(),
              done: widget.event?.done ?? false,
            );
            Navigator.pop(context, event);
          },
          child: const Text('Сохранить'),
        ),
      ],
    );
  }
}
