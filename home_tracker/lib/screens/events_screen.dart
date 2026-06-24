import 'package:flutter/material.dart';
import '../data/storage.dart';
import '../models/models.dart';
import '../widgets/event_dialog.dart';

class EventsScreen extends StatefulWidget {
  const EventsScreen({super.key});
  @override
  State<EventsScreen> createState() => _EventsScreenState();
}

class _EventsScreenState extends State<EventsScreen> {
  List<FamilyEvent> _events = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final e = await Storage.loadEvents();
    setState(() => _events = e);
  }

  Future<void> _toggle(String id) async {
    final idx = _events.indexWhere((e) => e.id == id);
    if (idx == -1) return;
    _events[idx].done = !_events[idx].done;
    await Storage.saveEvents(_events);
    setState(() {});
  }

  Future<void> _delete(String id) async {
    _events.removeWhere((e) => e.id == id);
    await Storage.saveEvents(_events);
    setState(() {});
  }

  Future<void> _showDialog(FamilyEvent? event) async {
    final result = await showDialog<FamilyEvent>(
      context: context,
      builder: (_) => EventDialog(event: event),
    );
    if (result == null) return;
    if (event == null) {
      _events.insert(0, result);
    } else {
      final idx = _events.indexWhere((e) => e.id == result.id);
      if (idx != -1) _events[idx] = result;
    }
    await Storage.saveEvents(_events);
    setState(() {});
  }

  static const _months = ['ЯНВАРЬ', 'ФЕВРАЛЬ', 'МАРТ', 'АПРЕЛЬ', 'МАЙ', 'ИЮНЬ',
    'ИЮЛЬ', 'АВГУСТ', 'СЕНТЯБРЬ', 'ОКТЯБРЬ', 'НОЯБРЬ', 'ДЕКАБРЬ'];

  String _monthKey(String date) {
    final d = DateTime.tryParse(date);
    if (d == null) return 'Без даты';
    return '${_months[d.month - 1]} ${d.year}';
  }

  Map<String, List<FamilyEvent>> get _grouped {
    final map = <String, List<FamilyEvent>>{};
    for (final e in _events) {
      final key = e.date.isEmpty ? 'Без даты' : _monthKey(e.date);
      map.putIfAbsent(key, () => []);
      map[key]!.add(e);
    }
    final sorted = map.entries.toList()..sort((a, b) {
      if (a.key == 'Без даты') return 1;
      if (b.key == 'Без даты') return -1;
      final ap = _parseMonthKey(a.key);
      final bp = _parseMonthKey(b.key);
      if (ap.$1 != bp.$1) return ap.$1.compareTo(bp.$1);
      return ap.$2.compareTo(bp.$2);
    });
    return {for (final e in sorted) e.key: e.value};
  }

  (int, int) _parseMonthKey(String key) {
    for (int i = 0; i < _months.length; i++) {
      if (key.startsWith(_months[i])) {
        final year = int.tryParse(key.substring(_months[i].length + 1)) ?? 0;
        return (year, i);
      }
    }
    return (0, 0);
  }

  static const _emojis = {
    'День рождения': '🎂', 'Поездка': '✈️', 'Свадьба': '💍',
    'Юбилей': '🎉', 'Праздник': '🎊', 'Встреча': '🤝', 'Другое': '📌',
  };

  @override
  Widget build(BuildContext context) {
    final grouped = _grouped;

    return Scaffold(
      appBar: AppBar(
        title: const Text('📅 События'),
        actions: [
          IconButton(icon: const Icon(Icons.add), onPressed: () => _showDialog(null)),
        ],
      ),
      body: grouped.isEmpty
          ? const Center(child: Text('Нет событий', style: TextStyle(color: Colors.grey)))
          : ListView(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              children: grouped.entries.map((entry) {
                final items = entry.value;
                items.sort((a, b) => a.done == b.done ? 0 : a.done ? 1 : -1);

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(top: 10, bottom: 4),
                      child: Text(entry.key,
                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF2D5A3E), letterSpacing: 0.5)),
                    ),
                    ...items.map((e) => _buildItem(e)),
                  ],
                );
              }).toList(),
            ),
    );
  }

  Widget _buildItem(FamilyEvent e) {
    final emoji = _emojis[e.type] ?? '📌';
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 2),
      child: ListTile(
        leading: Checkbox(value: e.done, onChanged: (_) => _toggle(e.id)),
        title: Text(
          '$emoji ${e.title}',
          style: TextStyle(fontWeight: FontWeight.w600, fontSize: 15,
            decoration: e.done ? TextDecoration.lineThrough : null),
        ),
        subtitle: Text(
          '${e.type}${e.date.isNotEmpty ? ' · 📅 ${e.date}' : ''}${e.time.isNotEmpty ? ' ${e.time}' : ''}${e.place.isNotEmpty ? ' · 📍 ${e.place}' : ''}${e.comment.isNotEmpty ? ' · 💬 ${e.comment}' : ''}',
          style: const TextStyle(fontSize: 13),
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(icon: const Icon(Icons.edit_outlined, size: 18), onPressed: () => _showDialog(e)),
            IconButton(icon: const Icon(Icons.delete_outline, size: 18, color: Colors.red), onPressed: () => _delete(e.id)),
          ],
        ),
      ),
    );
  }
}
