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
    List.new("default")
    |> List.with_items([
      Item.new("quake (b)", categories.lookup_by_short("b")),
      Item.new("doom (c)", categories.lookup_by_short("c")),
      Item.new("wolf3d (b)", categories.lookup_by_short("b")),
      Item.new("worms (a)", categories.lookup_by_short("a")),
      Item.new("call of duty (a)", categories.lookup_by_short("a")),
      Item.new("farcry (c)", categories.lookup_by_short("c"))
    ])
  end
end
