extends Control

# Эта функция сработает, когда нажмут первую кнопку (Играть)
func _on_button_pressed() -> void:
 get_tree().change_scene_to_file("res://node_3d.tscn")

# Эта функция сработает, когда нажмут вторую кнопку (Выход)
func _on_button_2_pressed() -> void:
 get_tree().quit()
