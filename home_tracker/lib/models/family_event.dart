class FamilyEvent {
  final String id;
  final String title;
  final String type;
  final String date;
  final String time;
  final String place;
  final String comment;
  bool done;

  FamilyEvent({
    required this.id,
    required this.title,
    this.type = 'Другое',
    this.date = '',
    this.time = '',
    this.place = '',
    this.comment = '',
    this.done = false,
  });

  Map<String, dynamic> toJson() => {
    'id': id, 'title': title, 'type': type, 'date': date,
    'time': time, 'place': place, 'comment': comment, 'done': done,
  };

  factory FamilyEvent.fromJson(Map<String, dynamic> j) => FamilyEvent(
    id: j['id'] as String,
    title: j['title'] as String,
    type: j['type'] as String? ?? 'Другое',
    date: j['date'] as String? ?? '',
    time: j['time'] as String? ?? '',
    place: j['place'] as String? ?? '',
    comment: j['comment'] as String? ?? '',
    done: j['done'] as bool? ?? false,
  );
}
