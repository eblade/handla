defmodule Builders do
  defmacro __using__(_options) do
    quote do
      alias Handla.Core.{Category, Categories, List, Item}
      import Builders, only: :functions
    end
  end

  alias Handla.Core.{Category, Categories, List, Item}

  def test_categories() do
    Categories.new([
      Category.new("Category A", "a", 0),
      Category.new("Category B", "b", 1),
      Category.new("Category C", "c", 2),
    ])
  end

  def test_games(categories) do
    list = List.new("default")
    List.with_items(list, [
      Item.new("quake (b)", Categories.lookup_by_short(categories, "b")),
      Item.new("doom (c)", Categories.lookup_by_short(categories, "c")),
      Item.new("wolf3d (b)", Categories.lookup_by_short(categories, "b")),
      Item.new("worms (a)", Categories.lookup_by_short(categories, "a")),
      Item.new("call of duty (a)", Categories.lookup_by_short(categories, "a")),
      Item.new("farcry (c)", Categories.lookup_by_short(categories, "c"))
    ])
  end
end
