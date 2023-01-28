defmodule Handla.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      { Handla.Boundary.ListSession,
        [name: Handla.Boundary.ListSession] }
    ]

    opts = [strategy: :one_for_one, name: Handla.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
