class Chore {
  final String id;
  final String title;
  final String category;
  final String assignee;
  final String date;
  final String priority;
  bool done;

  Chore({
    required this.id,
    required this.title,
    required this.category,
    this.assignee = 'Я',
    this.date = '',
    this.priority = 'Средний',
    this.done = false,
  });

  Map<String, dynamic> toJson() => {
    'id': id, 'title': title, 'category': category,
    'assignee': assignee, 'date': date, 'priority': priority, 'done': done,
  };

  factory Chore.fromJson(Map<String, dynamic> j) => Chore(
    id: j['id'] as String,
    title: j['title'] as String,
    category: j['category'] as String,
    assignee: j['assignee'] as String? ?? 'Я',
    date: j['date'] as String? ?? '',
    priority: j['priority'] as String? ?? 'Средний',
    done: j['done'] as bool? ?? false,
  );
}
