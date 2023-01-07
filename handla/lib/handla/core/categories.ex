defmodule Handla.Core.Categories do
  defstruct ~w[categories]a

  def new(categories) do
    %__MODULE__{
      categories: categories
    }
  end

  def lookup_by_short(categories, short) do
    Enum.find(categories.categories, &(&1.short == short))
  end
end
