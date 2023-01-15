defmodule Handla.Core.List do
  defstruct ~w[name items timestamp]a

  def new(name) do
    %__MODULE__{
      name: name,
      items: [],
      timestamp: DateTime.utc_now
    }
  end

  def with_items(list, items) do
    %__MODULE__{
      name: list.name,
      items: items,
      timestamp: DateTime.utc_now
    }
  end

  def sort(list) do
    %{list | items: Enum.sort_by(list.items, &({&1.category.ordinal,  &1.text}), :asc)}
  end

  def get(list, text, category_short) do
    Enum.find(list.items, &(&1.text == text && &1.category.short == category_short))
  end

  def add_new_item(list, item) do
    with_items(list, [item | list.items])
  end

  def replace(list, old_item, new_item) do
    with_items(list, Enum.map(list.items, fn item ->
      if(Handla.Core.Item.equals?(item, old_item), do: new_item, else: item) end))
  end
end
