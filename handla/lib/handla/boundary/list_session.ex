defmodule Handla.Boundary.ListSession do
  alias Handla.Core.{List, Item, Category, Categories}
  use GenServer

  def start_link(options \\ nil) do
    {list, categories} = case options do
      {list, categories} -> {list, categories}
      _ -> {List.new("Listan"), Categories.new([
        Category.new("grönsaker", "g", 0),
        Category.new("frukt", "r", 1),
        Category.new("bröd", "b", 2),
        Category.new("färdigmat", "f", 3),
        Category.new("kött", "k", 4),
        Category.new("mejeri", "m", 4),
        Category.new("fryst", "y", 5),
        Category.new("världsmat", "v", 6),
        Category.new("städ", "s", 7),
        Category.new("skafferi", "t", 8),
        Category.new("barn", "a", 9),
        Category.new("hygien", "h", 10),
        Category.new("sist", "ö", 11)
      ])}
    end
    GenServer.start_link(
      __MODULE__,
      {list, categories},
      name: __MODULE__
    )
  end

  def add_item(item) do
    GenServer.call(__MODULE__, {:add_item, item})
  end

  def check_item(item) do
    GenServer.call(__MODULE__, {:check_item, item})
  end

  def uncheck_item(item) do
    GenServer.call(__MODULE__, {:uncheck_item, item})
  end

  def get_categories() do
    GenServer.call(__MODULE__, :get_categories)
  end

  def init({list, categories}) do
    {:ok, {list, categories}}
  end

  def handle_call({:add_item, item}, _from, {list, categories}) do
    List.add_new_item(list, item)
    {:reply, item, {list, categories}}
  end

  def handle_call({:check_item, item}, _from, {list, categories}) do
    checked_item = Item.check(item)
    List.replace(list, item, checked_item)
    {:reply, checked_item, {list, categories}}
  end

  def handle_call({:uncheck_item, item}, _from, {list, categories}) do
    unchecked_item = Item.uncheck(item)
    List.replace(list, item, unchecked_item)
    {:reply, unchecked_item, {list, categories}}
  end

  def handle_call(:get_categories, _from, {list, categories}) do
    {:reply, categories, {list, categories}}
  end
end
