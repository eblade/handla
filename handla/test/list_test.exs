defmodule ListTest do
  use ExUnit.Case
  use Builders

  test "items are sorted by category ordinal, then name" do
    sorted = List.sort(test_games(test_categories()))
    assert Enum.at(sorted.items, 0).text == "call of duty (a)"
    assert Enum.at(sorted.items, 1).text == "worms (a)"
    assert Enum.at(sorted.items, 2).text == "quake (b)"
    assert Enum.at(sorted.items, 3).text == "wolf3d (b)"
    assert Enum.at(sorted.items, 4).text == "doom (c)"
    assert Enum.at(sorted.items, 5).text == "farcry (c)"
  end

  test "adding a new item leaves it unchecked" do
    categories = test_categories()
    items = test_games(categories)
    new_item = Item.new("chess", Categories.lookup_by_short(categories,"c"))
    items = List.add_new_item(items, new_item)
    same_item = List.get(items, "chess", "c")
    assert !same_item.checked
  end

  test "re-adding an old item makes it unchecked and removes any comment" do
    categories = test_categories()
    items = test_games(categories)
    item = List.get(items, "doom (c)", "c")
    assert item.checked
    items = List.replace(items, item, Item.reset(item))
    same_item = List.get(items, "doom (c)", "c")
    assert !same_item.checked
    assert same_item.comment == ""
  end
end
