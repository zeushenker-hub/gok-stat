class Category {
  final String name;
  Category(this.name);

  Map<String, dynamic> toJson() => {'name': name};
  static Category fromJson(Map<String, dynamic> json) => Category(json['name'] as String);
}
